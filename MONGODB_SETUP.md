# MongoDB Setup Guide for Student Management System

## 📋 Overview
This guide will help you set up MongoDB to enable the **Activity Logs & Audit Trail** feature in the Student Management System.

---

## 🛠️ Installation

### Windows (Recommended Methods)

#### Method 1: Using MongoDB Community Server (Recommended)

1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows x64, MSI package
   - Download the installer

2. **Install MongoDB**
   - Run the MSI installer
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service" (recommended)
   - Check "Install MongoDB Compass" (optional GUI tool)
   - Complete the installation

3. **Verify Installation**
   ```powershell
   mongod --version
   ```

4. **MongoDB Service Management**
   ```powershell
   # Check if service is running
   Get-Service MongoDB
   
   # Start MongoDB service
   Start-Service MongoDB
   
   # Stop MongoDB service
   Stop-Service MongoDB
   ```

#### Method 2: Using MongoDB Atlas (Cloud - Free Tier)

1. **Create MongoDB Atlas Account**
   - Visit: https://www.mongodb.com/cloud/atlas/register
   - Sign up for free tier (no credit card required)

2. **Create a Cluster**
   - Choose FREE tier (M0 Sandbox)
   - Select a cloud provider and region
   - Click "Create Cluster"

3. **Configure Database Access**
   - Go to "Database Access"
   - Add a new database user with username and password
   - Select "Read and write to any database"

4. **Configure Network Access**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Or add your specific IP address

5. **Get Connection String**
   - Go to "Clusters" → Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Example: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

---

## ⚙️ Configuration

### 1. Update Your .env File

Add these lines to your `.env` file:

#### For Local MongoDB:
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=student_management_logs
```

#### For MongoDB Atlas (Cloud):
```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=student_management_logs
```

#### For Docker:
```env
MONGODB_URI=mongodb://mongodb:27017/
MONGODB_DB_NAME=student_management_logs
```

**Note:** Replace `username`, `password`, and cluster URL with your actual credentials.

### 2. Verify pymongo is Installed

The `pymongo` package is already in `requirements.txt`. If you need to reinstall:

```powershell
pip install pymongo==4.6.1
```

---

## 🚀 Starting the Application

### 1. Start MongoDB (Local Only)

If using local MongoDB, ensure the service is running:

```powershell
# Check status
Get-Service MongoDB

# Start if not running
Start-Service MongoDB
```

### 2. Run Django Development Server

```powershell
python manage.py runserver
```

### 3. Check MongoDB Connection

When you start the server, you should see:
```
✓ Connected to MongoDB database: student_management_logs
```

If you see an error, MongoDB logging will be disabled but the app will still work.

---

## 📊 What Gets Logged?

The system automatically logs the following activities:

### User Authentication
- ✅ Login attempts (successful and failed)
- ✅ Logout actions
- ✅ User registrations (students and teachers)

### Enrollments
- ✅ Direct enrollments by teachers
- ✅ Enrollment request creation
- ✅ Enrollment request approvals
- ✅ Enrollment request rejections

### Academic Actions
- ✅ Grade updates (including before/after values)
- ✅ Course deadline changes

### Logged Information
Each log entry includes:
- **Timestamp** (UTC)
- **Action Type** (login, enrollment, grade_update, etc.)
- **User ID & Username**
- **User Type** (admin, teacher, student)
- **IP Address**
- **User Agent** (browser/device info)
- **Detailed Context** (student names, course info, grade changes, etc.)

---

## 🔍 Viewing Activity Logs

### Web Interface (Teachers & Admins)

1. **Login as Teacher or Admin**
2. **Navigate to Activity Logs**
   - From Teacher Dashboard → Click "Activity Logs" in Quick Actions
   - Or visit: `http://localhost:8000/activity-logs/`

3. **Filter Logs**
   - By Action Type (login, enrollment, grade_update, etc.)
   - Limit results (25, 50, 100, 200)
   - View detailed statistics

### API Endpoints

#### Get All Activity Logs (Teachers & Admins)
```http
GET /api/activity-logs/
```

Query parameters:
- `limit`: Number of logs (default: 50, max: 200)
- `action_type`: Filter by specific action
- `user_id`: Filter by user ID

Example:
```http
GET /api/activity-logs/?limit=100&action_type=login_success
```

#### Get Activity Statistics (Admins Only)
```http
GET /api/activity-logs/stats/
```

Query parameters:
- `days`: Number of days to analyze (default: 7)

#### Get My Activity Logs (All Authenticated Users)
```http
GET /api/activity-logs/my-logs/
```

---

## 🔧 Troubleshooting

### Problem: "Failed to connect to MongoDB"

**Solutions:**

1. **Check if MongoDB is running:**
   ```powershell
   Get-Service MongoDB
   # If stopped, start it:
   Start-Service MongoDB
   ```

2. **Verify MongoDB URI in .env:**
   - For local: `MONGODB_URI=mongodb://localhost:27017/`
   - For Atlas: Use the connection string from Atlas dashboard
   - For Docker: `MONGODB_URI=mongodb://mongodb:27017/`

3. **Test connection manually:**
   ```python
   python test_mongodb.py
   ```

4. **Check firewall settings:**
   - MongoDB uses port 27017 by default
   - Ensure it's not blocked by firewall

### Problem: MongoDB logs not appearing

**Check:**
- Is MongoDB connected? (Look for connection message in console)
- Are you logged in as teacher or admin?
- Try triggering an action (login, enroll a student, update grade)
- Visit `/activity-logs/` to see if logs appear

### Problem: "Permission denied" when viewing logs

**Solution:**
- Activity logs are only accessible to teachers and admins
- Students cannot view the activity logs page
- Ensure you're logged in with the correct account type

---

## 📚 Using MongoDB Compass (GUI Tool)

MongoDB Compass is a visual tool to explore your database.

### Connect to Local MongoDB
1. Open MongoDB Compass
2. Connection string: `mongodb://localhost:27017`
3. Click "Connect"

### View Collections
1. Select database: `student_management_logs`
2. Browse collections:
   - `activity_logs` - All system activities
   - `notification_logs` - Email logs

### Query Examples

**Find all login actions:**
```json
{ "action_type": { "$regex": "login" } }
```

**Find actions by specific user:**
```json
{ "user_id": 1 }
```

**Find actions in last 24 hours:**
```json
{ "timestamp": { "$gte": new Date(Date.now() - 24*60*60*1000) } }
```

---

## 🔐 Security Considerations

### Production Recommendations

1. **Secure MongoDB:**
   - Enable authentication
   - Use strong passwords
   - Limit network access
   - Enable TLS/SSL

2. **Protect Credentials:**
   - Never commit `.env` file
   - Use environment variables in production
   - Rotate credentials regularly

3. **Data Retention:**
   - Implement log rotation
   - Archive old logs (e.g., > 90 days)
   - Set up backup procedures

4. **Access Control:**
   - Only teachers and admins can view logs
   - API endpoints require authentication
   - Implement rate limiting

---

## 📖 Additional Resources

- [MongoDB Official Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas Free Tier](https://www.mongodb.com/cloud/atlas/register)
- [MongoDB Compass Download](https://www.mongodb.com/products/compass)

---

**The application will continue to work even if MongoDB is not connected - logging will simply be disabled.**

