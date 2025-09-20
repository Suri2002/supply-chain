import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [deliveryPerformance, setDeliveryPerformance] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [customerForm, setCustomerForm] = useState({ name: '', email: '', phone: '', address: '' });
  const [serviceForm, setServiceForm] = useState({ name: '', type: 'logistics', description: '', base_price: '', estimated_delivery_days: '' });
  const [bookingForm, setBookingForm] = useState({ customer_id: '', service_id: '', quantity: 1, notes: '' });
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [customersRes, servicesRes, bookingsRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/customers`),
        axios.get(`${API}/services`),
        axios.get(`${API}/bookings`),
        axios.get(`${API}/analytics/overview`)
      ]);
      
      setCustomers(customersRes.data);
      setServices(servicesRes.data);
      setBookings(bookingsRes.data);
      setAnalytics(analyticsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchDeliveryPerformance = async () => {
    try {
      const response = await axios.get(`${API}/analytics/delivery-performance`);
      setDeliveryPerformance(response.data);
    } catch (error) {
      console.error('Error fetching delivery performance:', error);
    }
  };

  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/customers`, customerForm);
      setCustomerForm({ name: '', email: '', phone: '', address: '' });
      fetchData();
      alert('Customer created successfully!');
    } catch (error) {
      alert('Error creating customer: ' + error.response?.data?.detail);
    }
    setLoading(false);
  };

  const handleServiceSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/services`, {
        ...serviceForm,
        base_price: parseFloat(serviceForm.base_price),
        estimated_delivery_days: parseInt(serviceForm.estimated_delivery_days)
      });
      setServiceForm({ name: '', type: 'logistics', description: '', base_price: '', estimated_delivery_days: '' });
      fetchData();
      alert('Service created successfully!');
    } catch (error) {
      alert('Error creating service: ' + error.response?.data?.detail);
    }
    setLoading(false);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/bookings`, {
        ...bookingForm,
        quantity: parseInt(bookingForm.quantity)
      });
      setBookingForm({ customer_id: '', service_id: '', quantity: 1, notes: '' });
      fetchData();
      alert('Booking created successfully!');
    } catch (error) {
      alert('Error creating booking: ' + error.response?.data?.detail);
    }
    setLoading(false);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      alert('Please select a file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await axios.post(`${API}/upload/bookings`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadResult(response.data);
      setUploadFile(null);
      fetchData();
    } catch (error) {
      alert('Error uploading file: ' + error.response?.data?.detail);
    }
    setLoading(false);
  };

  const updateBookingStatus = async (bookingId, status) => {
    setLoading(true);
    try {
      const updateData = { status };
      if (status === 'delivered') {
        updateData.actual_delivery_date = new Date().toISOString();
      }
      
      await axios.put(`${API}/bookings/${bookingId}`, updateData);
      fetchData();
      alert('Booking status updated!');
    } catch (error) {
      alert('Error updating booking: ' + error.response?.data?.detail);
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">Supply Chain Management</h1>
              <span className="ml-4 text-sm text-gray-500">Customer Booking & Analytics System</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex space-x-1 mb-8">
          {['overview', 'customers', 'services', 'bookings', 'upload', 'analytics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Total Customers</h3>
                <p className="text-3xl font-bold text-blue-600">{analytics.total_customers || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Total Services</h3>
                <p className="text-3xl font-bold text-green-600">{analytics.total_services || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Total Bookings</h3>
                <p className="text-3xl font-bold text-purple-600">{analytics.total_bookings || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">On-Time Delivery Rate</h3>
                <p className="text-3xl font-bold text-orange-600">{analytics.on_time_delivery_rate || 0}%</p>
              </div>
            </div>

            {/* Status Distribution */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Booking Status Distribution</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(analytics.status_counts || {}).map(([status, count]) => (
                  <div key={status} className="text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
                      {status.replace('_', ' ')}
                    </div>
                    <p className="text-2xl font-bold text-gray-700 mt-2">{count}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Customers Tab */}
        {activeTab === 'customers' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Customer</h3>
              <form onSubmit={handleCustomerSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Customer Name"
                  value={customerForm.name}
                  onChange={(e) => setCustomerForm({...customerForm, name: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={customerForm.email}
                  onChange={(e) => setCustomerForm({...customerForm, email: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <input
                  type="tel"
                  placeholder="Phone"
                  value={customerForm.phone}
                  onChange={(e) => setCustomerForm({...customerForm, phone: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                />
                <input
                  type="text"
                  placeholder="Address"
                  value={customerForm.address}
                  onChange={(e) => setCustomerForm({...customerForm, address: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="md:col-span-2 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Add Customer'}
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Customers ({customers.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {customers.map((customer) => (
                      <tr key={customer.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{customer.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.phone || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(customer.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Services Tab */}
        {activeTab === 'services' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Service</h3>
              <form onSubmit={handleServiceSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Service Name"
                  value={serviceForm.name}
                  onChange={(e) => setServiceForm({...serviceForm, name: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <select
                  value={serviceForm.type}
                  onChange={(e) => setServiceForm({...serviceForm, type: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="logistics">Logistics</option>
                  <option value="transportation">Transportation</option>
                  <option value="consulting">Consulting</option>
                </select>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Base Price"
                  value={serviceForm.base_price}
                  onChange={(e) => setServiceForm({...serviceForm, base_price: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <input
                  type="number"
                  placeholder="Estimated Delivery Days"
                  value={serviceForm.estimated_delivery_days}
                  onChange={(e) => setServiceForm({...serviceForm, estimated_delivery_days: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <textarea
                  placeholder="Description"
                  value={serviceForm.description}
                  onChange={(e) => setServiceForm({...serviceForm, description: e.target.value})}
                  className="md:col-span-2 border border-gray-300 rounded-lg px-3 py-2"
                  rows="3"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="md:col-span-2 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Add Service'}
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Services ({services.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Delivery Days</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {services.map((service) => (
                      <tr key={service.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{service.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            service.type === 'logistics' ? 'bg-blue-100 text-blue-800' :
                            service.type === 'transportation' ? 'bg-green-100 text-green-800' :
                            'bg-purple-100 text-purple-800'
                          }`}>
                            {service.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${service.base_price}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{service.estimated_delivery_days} days</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(service.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Bookings Tab */}
        {activeTab === 'bookings' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Booking</h3>
              <form onSubmit={handleBookingSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <select
                  value={bookingForm.customer_id}
                  onChange={(e) => setBookingForm({...bookingForm, customer_id: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="">Select Customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>{customer.name} ({customer.email})</option>
                  ))}
                </select>
                <select
                  value={bookingForm.service_id}
                  onChange={(e) => setBookingForm({...bookingForm, service_id: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="">Select Service</option>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>{service.name} (${service.base_price})</option>
                  ))}
                </select>
                <input
                  type="number"
                  min="1"
                  placeholder="Quantity"
                  value={bookingForm.quantity}
                  onChange={(e) => setBookingForm({...bookingForm, quantity: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <textarea
                  placeholder="Notes"
                  value={bookingForm.notes}
                  onChange={(e) => setBookingForm({...bookingForm, notes: e.target.value})}
                  className="border border-gray-300 rounded-lg px-3 py-2"
                  rows="2"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="md:col-span-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Booking'}
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Bookings ({bookings.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estimated Delivery</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {bookings.map((booking) => {
                      const customer = customers.find(c => c.id === booking.customer_id);
                      const service = services.find(s => s.id === booking.service_id);
                      return (
                        <tr key={booking.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {customer?.name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {service?.name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{booking.quantity}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${booking.total_price}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(booking.status)}`}>
                              {booking.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(booking.estimated_delivery_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {booking.status !== 'delivered' && booking.status !== 'cancelled' && (
                              <select
                                onChange={(e) => updateBookingStatus(booking.id, e.target.value)}
                                className="text-xs border border-gray-300 rounded px-2 py-1"
                                defaultValue=""
                              >
                                <option value="">Update Status</option>
                                <option value="confirmed">Confirmed</option>
                                <option value="in_progress">In Progress</option>
                                <option value="delivered">Delivered</option>
                                <option value="cancelled">Cancelled</option>
                              </select>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Bulk Booking Upload</h3>
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">CSV Format Requirements:</h4>
                <p className="text-sm text-gray-600 mb-2">Your CSV file should contain the following columns:</p>
                <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                  <li><strong>customer_name</strong> (required): Full name of the customer</li>
                  <li><strong>customer_email</strong> (required): Customer's email address</li>
                  <li><strong>service_name</strong> (required): Exact name of the service (must exist in system)</li>
                  <li><strong>quantity</strong> (optional): Number of services ordered (default: 1)</li>
                  <li><strong>notes</strong> (optional): Additional notes for the booking</li>
                </ul>
              </div>
              
              <form onSubmit={handleFileUpload} className="space-y-4">
                <div>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !uploadFile}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50"
                >
                  {loading ? 'Uploading...' : 'Upload Bookings'}
                </button>
              </form>

              {uploadResult && (
                <div className="mt-6 p-4 border rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Upload Results</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">{uploadResult.records_processed}</p>
                      <p className="text-sm text-gray-600">Records Processed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{uploadResult.successful_imports}</p>
                      <p className="text-sm text-gray-600">Successful</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-red-600">{uploadResult.failed_imports}</p>
                      <p className="text-sm text-gray-600">Failed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-gray-600">{uploadResult.errors.length}</p>
                      <p className="text-sm text-gray-600">Errors</p>
                    </div>
                  </div>
                  
                  {uploadResult.errors.length > 0 && (
                    <div>
                      <h5 className="font-medium text-red-700 mb-2">Errors:</h5>
                      <div className="bg-red-50 p-3 rounded max-h-40 overflow-y-auto">
                        {uploadResult.errors.map((error, index) => (
                          <p key={index} className="text-sm text-red-600">{error}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Delivery Performance Analytics</h3>
                <button
                  onClick={fetchDeliveryPerformance}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
                >
                  Load Performance Data
                </button>
              </div>

              {deliveryPerformance.length > 0 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900">Average Delivery Time</h4>
                      <p className="text-2xl font-bold text-blue-600">
                        {Math.round(deliveryPerformance.reduce((sum, item) => sum + item.actual_days, 0) / deliveryPerformance.length)} days
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900">On-Time Deliveries</h4>
                      <p className="text-2xl font-bold text-green-600">
                        {Math.round((deliveryPerformance.filter(item => item.on_time).length / deliveryPerformance.length) * 100)}%
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900">Average Variance</h4>
                      <p className="text-2xl font-bold text-orange-600">
                        {Math.round(deliveryPerformance.reduce((sum, item) => sum + item.variance_days, 0) / deliveryPerformance.length)} days
                      </p>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Booking ID</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estimated Days</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual Days</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">On Time</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {deliveryPerformance.map((item) => (
                          <tr key={item.booking_id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                              {item.booking_id.slice(-8)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{Math.round(item.estimated_days)}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{Math.round(item.actual_days)}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <span className={item.variance_days > 0 ? 'text-red-600' : 'text-green-600'}>
                                {item.variance_days > 0 ? '+' : ''}{Math.round(item.variance_days)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                item.on_time ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {item.on_time ? 'Yes' : 'No'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;