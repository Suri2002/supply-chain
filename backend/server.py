from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import pandas as pd
import io
import csv
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ServiceType(str, Enum):
    LOGISTICS = "logistics"
    TRANSPORTATION = "transportation"  
    CONSULTING = "consulting"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Database Models
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: ServiceType
    description: Optional[str] = None
    base_price: float
    estimated_delivery_days: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceCreate(BaseModel):
    name: str
    type: ServiceType
    description: Optional[str] = None
    base_price: float
    estimated_delivery_days: int

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    service_id: str
    quantity: int = 1
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    estimated_delivery_date: datetime
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingCreate(BaseModel):
    customer_id: str
    service_id: str
    quantity: int = 1
    notes: Optional[str] = None

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class DeliveryPerformance(BaseModel):
    booking_id: str
    estimated_days: int
    actual_days: Optional[int] = None
    variance_days: Optional[int] = None
    on_time: Optional[bool] = None

class FileUploadResult(BaseModel):
    filename: str
    records_processed: int
    successful_imports: int
    failed_imports: int
    errors: List[str] = []

# Helper functions
def prepare_for_mongo(data):
    """Convert datetime objects to strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse datetime strings back from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith('_at') or key.endswith('_date'):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

# API Endpoints

# Customer Management
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_obj = Customer(**customer.dict())
    customer_dict = prepare_for_mongo(customer_obj.dict())
    await db.customers.insert_one(customer_dict)
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().to_list(1000)
    return [Customer(**parse_from_mongo(customer)) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**parse_from_mongo(customer))

# Service Management
@api_router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate):
    service_obj = Service(**service.dict())
    service_dict = prepare_for_mongo(service_obj.dict())
    await db.services.insert_one(service_dict)
    return service_obj

@api_router.get("/services", response_model=List[Service])
async def get_services():
    services = await db.services.find().to_list(1000)
    return [Service(**parse_from_mongo(service)) for service in services]

@api_router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: str):
    service = await db.services.find_one({"id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return Service(**parse_from_mongo(service))

# Booking Management
@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking: BookingCreate):
    # Validate customer and service exist
    customer = await db.customers.find_one({"id": booking.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    service = await db.services.find_one({"id": booking.service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Calculate total price and estimated delivery
    service_obj = Service(**parse_from_mongo(service))
    total_price = service_obj.base_price * booking.quantity
    estimated_delivery = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    estimated_delivery = estimated_delivery.replace(day=estimated_delivery.day + service_obj.estimated_delivery_days)
    
    booking_obj = Booking(
        **booking.dict(),
        total_price=total_price,
        estimated_delivery_date=estimated_delivery
    )
    
    booking_dict = prepare_for_mongo(booking_obj.dict())
    await db.bookings.insert_one(booking_dict)
    return booking_obj

@api_router.get("/bookings", response_model=List[Booking])
async def get_bookings(status: Optional[BookingStatus] = None):
    filter_query = {}
    if status:
        filter_query["status"] = status.value
    
    bookings = await db.bookings.find(filter_query).to_list(1000)
    return [Booking(**parse_from_mongo(booking)) for booking in bookings]

@api_router.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return Booking(**parse_from_mongo(booking))

@api_router.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(booking_id: str, booking_update: BookingUpdate):
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    update_data = {k: v for k, v in booking_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Calculate delivery performance if marking as delivered
    if booking_update.status == BookingStatus.DELIVERED and booking_update.actual_delivery_date:
        booking_obj = Booking(**parse_from_mongo(booking))
        estimated_days = (booking_obj.estimated_delivery_date.date() - booking_obj.created_at.date()).days
        actual_days = (booking_update.actual_delivery_date.date() - booking_obj.created_at.date()).days
        update_data["delivery_variance_days"] = actual_days - estimated_days
        update_data["delivered_on_time"] = actual_days <= estimated_days
    
    prepare_for_mongo(update_data)
    await db.bookings.update_one({"id": booking_id}, {"$set": update_data})
    
    updated_booking = await db.bookings.find_one({"id": booking_id})
    return Booking(**parse_from_mongo(updated_booking))

# File Upload for Bulk Booking Import
@api_router.post("/upload/bookings", response_model=FileUploadResult)
async def upload_bookings(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Expected columns: customer_name, customer_email, service_name, quantity, notes
        required_columns = ['customer_name', 'customer_email', 'service_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        successful_imports = 0
        failed_imports = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Find or create customer
                customer = await db.customers.find_one({"email": row['customer_email']})
                if not customer:
                    customer_data = CustomerCreate(
                        name=row['customer_name'],
                        email=row['customer_email']
                    )
                    customer_obj = Customer(**customer_data.dict())
                    customer_dict = prepare_for_mongo(customer_obj.dict())
                    await db.customers.insert_one(customer_dict)
                    customer_id = customer_obj.id
                else:
                    customer_id = customer['id']
                
                # Find service
                service = await db.services.find_one({"name": row['service_name']})
                if not service:
                    errors.append(f"Row {index + 1}: Service '{row['service_name']}' not found")
                    failed_imports += 1
                    continue
                
                # Create booking
                booking_data = BookingCreate(
                    customer_id=customer_id,
                    service_id=service['id'],
                    quantity=int(row.get('quantity', 1)),
                    notes=row.get('notes', '')
                )
                
                # Calculate booking details
                service_obj = Service(**parse_from_mongo(service))
                total_price = service_obj.base_price * booking_data.quantity
                estimated_delivery = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                estimated_delivery = estimated_delivery.replace(day=estimated_delivery.day + service_obj.estimated_delivery_days)
                
                booking_obj = Booking(
                    **booking_data.dict(),
                    total_price=total_price,
                    estimated_delivery_date=estimated_delivery
                )
                
                booking_dict = prepare_for_mongo(booking_obj.dict())
                await db.bookings.insert_one(booking_dict)
                successful_imports += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                failed_imports += 1
        
        return FileUploadResult(
            filename=file.filename,
            records_processed=len(df),
            successful_imports=successful_imports,
            failed_imports=failed_imports,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Analytics Endpoints
@api_router.get("/analytics/delivery-performance")
async def get_delivery_performance():
    # Get delivered bookings with actual delivery dates
    delivered_bookings = await db.bookings.find({
        "status": "delivered",
        "actual_delivery_date": {"$exists": True}
    }).to_list(1000)
    
    performance_data = []
    
    for booking in delivered_bookings:
        try:
            # Get the service details
            service = await db.services.find_one({"id": booking["service_id"]})
            if not service:
                continue
            
            # Parse dates
            booking_obj = Booking(**parse_from_mongo(booking))
            service_obj = Service(**parse_from_mongo(service))
            
            # Calculate actual days from creation to delivery
            actual_days = (booking_obj.actual_delivery_date.date() - booking_obj.created_at.date()).days
            estimated_days = service_obj.estimated_delivery_days
            variance_days = actual_days - estimated_days
            on_time = actual_days <= estimated_days
            
            performance_data.append({
                "booking_id": booking_obj.id,
                "estimated_days": estimated_days,
                "actual_days": actual_days,
                "variance_days": variance_days,
                "on_time": on_time
            })
            
        except Exception as e:
            # Skip problematic records
            continue
    
    return performance_data

@api_router.get("/analytics/overview")
async def get_analytics_overview():
    # Get booking counts by status
    status_counts = await db.bookings.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(10)
    
    # Get on-time delivery rate
    delivery_stats = await db.bookings.aggregate([
        {
            "$match": {
                "status": "delivered",
                "delivered_on_time": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_delivered": {"$sum": 1},
                "on_time_deliveries": {
                    "$sum": {"$cond": [{"$eq": ["$delivered_on_time", True]}, 1, 0]}
                }
            }
        }
    ]).to_list(1)
    
    on_time_rate = 0
    if delivery_stats:
        on_time_rate = (delivery_stats[0]["on_time_deliveries"] / delivery_stats[0]["total_delivered"]) * 100
    
    return {
        "status_counts": {item["_id"]: item["count"] for item in status_counts},
        "on_time_delivery_rate": round(on_time_rate, 2),
        "total_customers": await db.customers.count_documents({}),
        "total_services": await db.services.count_documents({}),
        "total_bookings": await db.bookings.count_documents({})
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()