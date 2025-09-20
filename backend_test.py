import requests
import json
import io
import csv
from datetime import datetime, timezone
import time

# Backend URL from frontend .env
BASE_URL = "https://funny-wilson.preview.emergentagent.com/api"

class SupplyChainAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.created_customers = []
        self.created_services = []
        self.created_bookings = []
        
    def log_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        print()
    
    def test_customer_management(self):
        """Test Customer CRUD operations"""
        print("=== TESTING CUSTOMER MANAGEMENT API ===")
        
        # Test 1: Create Customer
        customer_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techcorp.com",
            "phone": "+1-555-0123",
            "address": "123 Business Ave, Tech City, TC 12345"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.created_customers.append(customer['id'])
                self.log_test("Create Customer", True, f"Created customer: {customer['name']} (ID: {customer['id']})")
            else:
                self.log_test("Create Customer", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Customer", False, f"Exception: {str(e)}")
            return False
        
        # Test 2: Get All Customers
        try:
            response = self.session.get(f"{self.base_url}/customers")
            if response.status_code == 200:
                customers = response.json()
                self.log_test("Get All Customers", True, f"Retrieved {len(customers)} customers")
            else:
                self.log_test("Get All Customers", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Customers", False, f"Exception: {str(e)}")
            return False
        
        # Test 3: Get Specific Customer
        if self.created_customers:
            try:
                customer_id = self.created_customers[0]
                response = self.session.get(f"{self.base_url}/customers/{customer_id}")
                if response.status_code == 200:
                    customer = response.json()
                    self.log_test("Get Specific Customer", True, f"Retrieved customer: {customer['name']}")
                else:
                    self.log_test("Get Specific Customer", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Get Specific Customer", False, f"Exception: {str(e)}")
                return False
        
        return True
    
    def test_service_management(self):
        """Test Service CRUD operations with different service types"""
        print("=== TESTING SERVICE MANAGEMENT API ===")
        
        # Test 1: Create Logistics Service
        logistics_service = {
            "name": "Express Freight Delivery",
            "type": "logistics",
            "description": "Fast freight delivery service for urgent shipments",
            "base_price": 150.00,
            "estimated_delivery_days": 3
        }
        
        try:
            response = self.session.post(f"{self.base_url}/services", json=logistics_service)
            if response.status_code == 200:
                service = response.json()
                self.created_services.append(service['id'])
                self.log_test("Create Logistics Service", True, f"Created service: {service['name']} (Type: {service['type']})")
            else:
                self.log_test("Create Logistics Service", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Logistics Service", False, f"Exception: {str(e)}")
            return False
        
        # Test 2: Create Transportation Service
        transport_service = {
            "name": "Long Haul Transportation",
            "type": "transportation",
            "description": "Cross-country transportation service",
            "base_price": 500.00,
            "estimated_delivery_days": 7
        }
        
        try:
            response = self.session.post(f"{self.base_url}/services", json=transport_service)
            if response.status_code == 200:
                service = response.json()
                self.created_services.append(service['id'])
                self.log_test("Create Transportation Service", True, f"Created service: {service['name']} (Type: {service['type']})")
            else:
                self.log_test("Create Transportation Service", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Transportation Service", False, f"Exception: {str(e)}")
            return False
        
        # Test 3: Create Consulting Service
        consulting_service = {
            "name": "Supply Chain Optimization",
            "type": "consulting",
            "description": "Expert consulting for supply chain efficiency",
            "base_price": 2000.00,
            "estimated_delivery_days": 14
        }
        
        try:
            response = self.session.post(f"{self.base_url}/services", json=consulting_service)
            if response.status_code == 200:
                service = response.json()
                self.created_services.append(service['id'])
                self.log_test("Create Consulting Service", True, f"Created service: {service['name']} (Type: {service['type']})")
            else:
                self.log_test("Create Consulting Service", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Consulting Service", False, f"Exception: {str(e)}")
            return False
        
        # Test 4: Get All Services
        try:
            response = self.session.get(f"{self.base_url}/services")
            if response.status_code == 200:
                services = response.json()
                self.log_test("Get All Services", True, f"Retrieved {len(services)} services")
            else:
                self.log_test("Get All Services", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Services", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_booking_management(self):
        """Test Booking CRUD operations with price calculation and delivery estimation"""
        print("=== TESTING BOOKING MANAGEMENT API ===")
        
        if not self.created_customers or not self.created_services:
            self.log_test("Booking Management Prerequisites", False, "Need customers and services first")
            return False
        
        # Test 1: Create Booking
        booking_data = {
            "customer_id": self.created_customers[0],
            "service_id": self.created_services[0],
            "quantity": 2,
            "notes": "Urgent delivery required for Q4 inventory"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/bookings", json=booking_data)
            if response.status_code == 200:
                booking = response.json()
                self.created_bookings.append(booking['id'])
                self.log_test("Create Booking", True, 
                    f"Created booking (ID: {booking['id']}) - Total: ${booking['total_price']}, "
                    f"Est. Delivery: {booking['estimated_delivery_date']}")
            else:
                self.log_test("Create Booking", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Booking", False, f"Exception: {str(e)}")
            return False
        
        # Test 2: Get All Bookings
        try:
            response = self.session.get(f"{self.base_url}/bookings")
            if response.status_code == 200:
                bookings = response.json()
                self.log_test("Get All Bookings", True, f"Retrieved {len(bookings)} bookings")
            else:
                self.log_test("Get All Bookings", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Bookings", False, f"Exception: {str(e)}")
            return False
        
        # Test 3: Update Booking Status to Delivered
        if self.created_bookings:
            try:
                booking_id = self.created_bookings[0]
                update_data = {
                    "status": "delivered",
                    "actual_delivery_date": datetime.now(timezone.utc).isoformat()
                }
                
                response = self.session.put(f"{self.base_url}/bookings/{booking_id}", json=update_data)
                if response.status_code == 200:
                    updated_booking = response.json()
                    self.log_test("Update Booking Status", True, 
                        f"Updated booking to delivered status - Actual delivery: {updated_booking.get('actual_delivery_date', 'N/A')}")
                else:
                    self.log_test("Update Booking Status", False, f"Status: {response.status_code}, Response: {response.text}")
                    return False
            except Exception as e:
                self.log_test("Update Booking Status", False, f"Exception: {str(e)}")
                return False
        
        # Test 4: Get Bookings by Status
        try:
            response = self.session.get(f"{self.base_url}/bookings?status=delivered")
            if response.status_code == 200:
                delivered_bookings = response.json()
                self.log_test("Get Bookings by Status", True, f"Retrieved {len(delivered_bookings)} delivered bookings")
            else:
                self.log_test("Get Bookings by Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Bookings by Status", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_file_upload(self):
        """Test bulk booking import from CSV file"""
        print("=== TESTING FILE UPLOAD FOR BULK BOOKINGS ===")
        
        if not self.created_services:
            self.log_test("File Upload Prerequisites", False, "Need services first")
            return False
        
        # Create CSV content for testing
        csv_content = """customer_name,customer_email,service_name,quantity,notes
Michael Chen,michael.chen@globaltech.com,Express Freight Delivery,1,Priority shipment for new product launch
Jennifer Rodriguez,j.rodriguez@innovatecorp.com,Long Haul Transportation,3,Quarterly inventory restocking
David Kim,david.kim@startupventures.com,Supply Chain Optimization,1,Consultation for scaling operations"""
        
        try:
            # Create a file-like object
            csv_file = io.StringIO(csv_content)
            files = {'file': ('bulk_bookings.csv', csv_file.getvalue(), 'text/csv')}
            
            response = self.session.post(f"{self.base_url}/upload/bookings", files=files)
            if response.status_code == 200:
                result = response.json()
                self.log_test("File Upload - CSV Processing", True, 
                    f"Processed {result['records_processed']} records, "
                    f"Successful: {result['successful_imports']}, "
                    f"Failed: {result['failed_imports']}")
                
                if result['errors']:
                    print(f"    Errors: {result['errors']}")
            else:
                self.log_test("File Upload - CSV Processing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("File Upload - CSV Processing", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_analytics(self):
        """Test analytics endpoints for delivery performance"""
        print("=== TESTING ANALYTICS ENDPOINTS ===")
        
        # Test 1: Get Delivery Performance Analytics
        try:
            response = self.session.get(f"{self.base_url}/analytics/delivery-performance")
            if response.status_code == 200:
                performance_data = response.json()
                self.log_test("Delivery Performance Analytics", True, 
                    f"Retrieved performance data for {len(performance_data)} delivered bookings")
            else:
                self.log_test("Delivery Performance Analytics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delivery Performance Analytics", False, f"Exception: {str(e)}")
            return False
        
        # Test 2: Get Overview Analytics
        try:
            response = self.session.get(f"{self.base_url}/analytics/overview")
            if response.status_code == 200:
                overview = response.json()
                self.log_test("Overview Analytics", True, 
                    f"Total customers: {overview.get('total_customers', 0)}, "
                    f"Total services: {overview.get('total_services', 0)}, "
                    f"Total bookings: {overview.get('total_bookings', 0)}, "
                    f"On-time delivery rate: {overview.get('on_time_delivery_rate', 0)}%")
            else:
                self.log_test("Overview Analytics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Overview Analytics", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("=== TESTING ERROR HANDLING ===")
        
        # Test 1: Get non-existent customer
        try:
            response = self.session.get(f"{self.base_url}/customers/non-existent-id")
            if response.status_code == 404:
                self.log_test("Error Handling - Non-existent Customer", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Non-existent Customer", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Non-existent Customer", False, f"Exception: {str(e)}")
        
        # Test 2: Create booking with invalid customer
        try:
            invalid_booking = {
                "customer_id": "invalid-customer-id",
                "service_id": self.created_services[0] if self.created_services else "invalid-service-id",
                "quantity": 1
            }
            response = self.session.post(f"{self.base_url}/bookings", json=invalid_booking)
            if response.status_code == 404:
                self.log_test("Error Handling - Invalid Customer in Booking", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Invalid Customer in Booking", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Customer in Booking", False, f"Exception: {str(e)}")
        
        # Test 3: Upload invalid file type
        try:
            files = {'file': ('test.txt', 'invalid content', 'text/plain')}
            response = self.session.post(f"{self.base_url}/upload/bookings", files=files)
            if response.status_code == 400:
                self.log_test("Error Handling - Invalid File Type", True, "Correctly returned 400")
            else:
                self.log_test("Error Handling - Invalid File Type", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid File Type", False, f"Exception: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 STARTING SUPPLY CHAIN MANAGEMENT API TESTS")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        test_results = {
            "Customer Management": self.test_customer_management(),
            "Service Management": self.test_service_management(),
            "Booking Management": self.test_booking_management(),
            "File Upload": self.test_file_upload(),
            "Analytics": self.test_analytics(),
            "Error Handling": self.test_error_handling()
        }
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Supply Chain Management API is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the detailed output above.")
        
        return passed == total

if __name__ == "__main__":
    tester = SupplyChainAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)