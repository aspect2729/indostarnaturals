# Owner Admin Guide

This guide explains how to use the IndoStar Naturals admin interface to manage your e-commerce platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Product Management](#product-management)
3. [Inventory Management](#inventory-management)
4. [Order Management](#order-management)
5. [User Management](#user-management)
6. [Subscription Management](#subscription-management)
7. [Analytics and Reports](#analytics-and-reports)
8. [Audit Logs](#audit-logs)
9. [Best Practices](#best-practices)

## Getting Started

### First Login

1. Navigate to the application URL
2. Click "Login" in the header
3. Enter your owner credentials:
   - Phone: +919999999999
   - Password: admin123
4. **IMPORTANT**: Change your password immediately after first login

### Changing Your Password

1. Go to Profile → Settings
2. Click "Change Password"
3. Enter current password and new password
4. Click "Update Password"

### Dashboard Overview

After logging in, you'll see the owner dashboard with:

- **Total Revenue**: Revenue from all paid orders
- **Order Count**: Total number of orders
- **Active Subscriptions**: Number of active milk subscriptions
- **Low Stock Alerts**: Products running low on inventory
- **Revenue Chart**: Daily/weekly/monthly revenue trends
- **Recent Orders**: Latest orders requiring attention

## Product Management

### Adding a New Product

1. Navigate to **Products** → **Add Product**
2. Fill in the required fields:
   - **Title**: Product name (e.g., "Organic Jaggery")
   - **Description**: Detailed product description
   - **Category**: Select from dropdown
   - **SKU**: Unique product code (e.g., "JAG-001")
   - **Unit Size**: Package size (e.g., "1kg", "500ml")
   - **Consumer Price**: Retail price for consumers
   - **Distributor Price**: Wholesale price for distributors
   - **Stock Quantity**: Initial inventory count
   - **Subscription Available**: Check if product can be subscribed to
3. Click "Save Product"

### Uploading Product Images

1. Go to **Products** → Select product → **Images**
2. Click "Upload Image"
3. Select image file (JPEG, PNG, or WebP, max 5MB)
4. Add alt text for accessibility
5. Set display order (1 = first image shown)
6. Click "Upload"

**Image Guidelines**:
- Use high-quality images (minimum 800x800px)
- Show product from multiple angles
- Use consistent lighting and background
- First image is the primary product image
- Optimize images before upload for faster loading

### Editing Products

1. Go to **Products** → Click on product
2. Click "Edit Product"
3. Update any fields
4. Click "Save Changes"

**Note**: Price changes are logged in audit logs for tracking.

### Deleting Products

1. Go to **Products** → Click on product
2. Click "Delete Product"
3. Confirm deletion

**Note**: This is a soft delete - the product is hidden but data is retained.

### Managing Categories

1. Go to **Products** → **Categories**
2. Click "Add Category"
3. Enter category name and slug
4. Select parent category (if subcategory)
5. Set display order
6. Click "Save"

**Category Best Practices**:
- Keep category names short and clear
- Use logical hierarchy (e.g., Milk Products → Ghee)
- Limit to 2-3 levels of nesting
- Use descriptive slugs (e.g., "organic-jaggery")

## Inventory Management

### Viewing Inventory

1. Go to **Inventory**
2. View all products with current stock levels
3. Filter by category or search by name/SKU
4. Sort by stock level to find low stock items

### Updating Stock

**Method 1: Individual Product**
1. Go to **Products** → Select product
2. Click "Update Stock"
3. Enter quantity to add or remove (use negative for removal)
4. Add notes (optional)
5. Click "Update"

**Method 2: Bulk Update**
1. Go to **Inventory** → **Bulk Update**
2. Upload CSV file with format:
   ```
   SKU,Quantity
   JAG-001,50
   MILK-001,-10
   ```
3. Click "Process"

### Low Stock Alerts

The dashboard shows products with stock below threshold (default: 10 units).

**To adjust threshold**:
1. Go to **Settings** → **Inventory**
2. Set "Low Stock Threshold"
3. Click "Save"

### Stock Audit Trail

All stock changes are logged:
1. Go to **Audit Logs**
2. Filter by "STOCK_UPDATED"
3. View who changed stock, when, and by how much

## Order Management

### Viewing Orders

1. Go to **Orders**
2. View all orders with status, customer, and amount
3. Filter by:
   - Status (pending, confirmed, packed, etc.)
   - Date range
   - User role (consumer, distributor)
   - Payment status

### Order Details

Click on any order to view:
- Order number and date
- Customer information
- Delivery address
- Order items with quantities and prices
- Payment status and method
- Order status history

### Updating Order Status

1. Open order details
2. Click "Update Status"
3. Select new status:
   - **Pending**: Order placed, awaiting confirmation
   - **Confirmed**: Payment received, ready to process
   - **Packed**: Order packed and ready for dispatch
   - **Out for Delivery**: Order shipped
   - **Delivered**: Order delivered to customer
   - **Cancelled**: Order cancelled
   - **Refunded**: Payment refunded
4. Add notes (optional)
5. Click "Update"

**Note**: Customer receives email notification on status change.

### Processing Refunds

1. Open order details
2. Click "Process Refund"
3. Enter refund reason
4. Confirm refund
5. Refund is processed through Razorpay

**Refund Timeline**:
- Refund initiated immediately
- Razorpay processes within 5-7 business days
- Customer receives email confirmation

### Bulk Order Actions

1. Go to **Orders**
2. Select multiple orders (checkbox)
3. Choose action:
   - Update status
   - Export to CSV
   - Print packing slips
4. Click "Apply"

## User Management

### Viewing Users

1. Go to **Users**
2. View all registered users
3. Filter by:
   - Role (consumer, distributor, owner)
   - Account status (active, inactive)
   - Registration date

### User Details

Click on any user to view:
- Contact information
- Role and permissions
- Registration date
- Order history
- Subscription history

### Approving Distributors

When users register as distributors, they require approval:

1. Go to **Users** → **Pending Distributors**
2. Review distributor application
3. Click "Approve" or "Reject"
4. Add notes (optional)
5. Confirm action

**Approved distributors**:
- Can see distributor prices
- Can place bulk orders
- Receive bulk discount benefits

### Changing User Roles

1. Open user details
2. Click "Change Role"
3. Select new role:
   - **Consumer**: Regular customer
   - **Distributor**: Wholesale customer
   - **Owner**: Admin access (use carefully!)
4. Confirm change

**Warning**: Changing roles affects pricing and permissions immediately.

### Deactivating Users

1. Open user details
2. Click "Deactivate Account"
3. Enter reason
4. Confirm

**Note**: Deactivated users cannot log in but data is retained.

## Subscription Management

### Viewing Subscriptions

1. Go to **Subscriptions**
2. View all active subscriptions
3. Filter by:
   - Status (active, paused, cancelled)
   - Product
   - Frequency (daily, alternate days, weekly)

### Subscription Calendar

1. Go to **Subscriptions** → **Calendar**
2. View scheduled deliveries by date
3. Click on date to see all deliveries
4. Export delivery schedule

**Use Cases**:
- Plan daily milk deliveries
- Coordinate with delivery partners
- Manage inventory for subscriptions

### Managing Subscriptions

While customers manage their own subscriptions, you can:

1. View subscription details
2. See payment history
3. Check delivery schedule
4. View cancellation reasons (if cancelled)

## Analytics and Reports

### Dashboard Metrics

The dashboard shows key metrics:
- **Total Revenue**: All-time revenue
- **Revenue Today**: Today's revenue
- **Orders Today**: Today's order count
- **Active Subscriptions**: Current active subscriptions
- **Average Order Value**: Revenue / Orders

### Revenue Reports

1. Go to **Analytics** → **Revenue**
2. Select date range
3. View:
   - Daily/weekly/monthly revenue
   - Revenue by product category
   - Revenue by user role (consumer vs distributor)
   - Payment method breakdown
4. Export to CSV or PDF

### Product Performance

1. Go to **Analytics** → **Products**
2. View:
   - Best-selling products
   - Revenue by product
   - Stock turnover rate
   - Products with no sales
3. Use insights to:
   - Reorder popular items
   - Discontinue slow-moving products
   - Adjust pricing

### Customer Analytics

1. Go to **Analytics** → **Customers**
2. View:
   - New customers this month
   - Repeat customer rate
   - Customer lifetime value
   - Geographic distribution
3. Use insights for marketing

### Subscription Analytics

1. Go to **Analytics** → **Subscriptions**
2. View:
   - Subscription growth rate
   - Churn rate
   - Revenue from subscriptions
   - Popular subscription frequencies
3. Identify trends and optimize offerings

## Audit Logs

### Viewing Audit Logs

1. Go to **Audit Logs**
2. View all system changes
3. Filter by:
   - Action type (product created, price updated, etc.)
   - Date range
   - User (who made the change)
   - Object type (product, order, user)

### Common Audit Events

- **PRODUCT_CREATED**: New product added
- **PRICE_UPDATED**: Product price changed
- **STOCK_UPDATED**: Inventory adjusted
- **ORDER_STATUS_CHANGED**: Order status updated
- **USER_ROLE_CHANGED**: User role modified
- **PAYMENT_PROCESSED**: Payment completed

### Using Audit Logs

**Compliance**:
- Track all price changes
- Monitor inventory adjustments
- Audit user access changes

**Troubleshooting**:
- Find when stock was last updated
- See who changed order status
- Track payment issues

**Security**:
- Monitor unauthorized access attempts
- Review admin actions
- Detect suspicious activity

## Best Practices

### Product Management

1. **Use Clear Titles**: Make product names descriptive
2. **Write Detailed Descriptions**: Include ingredients, benefits, usage
3. **Set Accurate Stock**: Update inventory regularly
4. **Use High-Quality Images**: Professional photos increase sales
5. **Consistent Pricing**: Review prices regularly for competitiveness

### Inventory Management

1. **Set Reorder Points**: Know when to restock
2. **Monitor Low Stock**: Check dashboard daily
3. **Audit Regularly**: Verify physical stock matches system
4. **Plan for Seasonality**: Stock up before peak seasons
5. **Track Expiry Dates**: For perishable items (not in system, track manually)

### Order Management

1. **Process Orders Quickly**: Update status within 24 hours
2. **Communicate Delays**: Notify customers of any issues
3. **Pack Carefully**: Ensure products arrive safely
4. **Track Deliveries**: Monitor delivery success rate
5. **Handle Returns Promptly**: Process refunds quickly

### Customer Service

1. **Respond Quickly**: Reply to inquiries within 24 hours
2. **Be Professional**: Maintain courteous communication
3. **Resolve Issues**: Address complaints promptly
4. **Follow Up**: Check customer satisfaction after delivery
5. **Build Relationships**: Encourage repeat business

### Security

1. **Use Strong Passwords**: Change default password immediately
2. **Limit Owner Access**: Only trusted staff should have owner role
3. **Review Audit Logs**: Check for suspicious activity weekly
4. **Backup Data**: Ensure regular backups are running
5. **Update Software**: Keep system updated with latest security patches

### Performance

1. **Optimize Images**: Compress images before upload
2. **Monitor Load Times**: Check site speed regularly
3. **Clean Up Data**: Archive old orders periodically
4. **Review Analytics**: Use data to improve operations
5. **Plan Capacity**: Scale infrastructure as business grows

## Troubleshooting

### Can't Upload Images

- Check file size (max 5MB)
- Verify file format (JPEG, PNG, WebP only)
- Try different browser
- Check internet connection

### Orders Not Updating

- Verify payment webhook is configured
- Check Razorpay dashboard for payment status
- Review error logs
- Contact technical support

### Stock Discrepancies

- Review audit logs for recent changes
- Check for pending orders
- Verify bulk update CSV format
- Conduct physical inventory count

### Reports Not Loading

- Try smaller date range
- Clear browser cache
- Check internet connection
- Try different browser

## Getting Help

### Support Channels

- **Email**: support@indostarnaturals.com
- **Phone**: +91-XXXX-XXXXXX
- **Documentation**: https://docs.indostarnaturals.com
- **Status Page**: https://status.indostarnaturals.com

### Before Contacting Support

1. Check this guide
2. Review error message
3. Try in different browser
4. Clear cache and cookies
5. Note steps to reproduce issue

### Information to Provide

- Your user ID
- Browser and version
- Screenshot of error
- Steps to reproduce
- Date and time of issue

## Appendix

### Keyboard Shortcuts

- `Ctrl/Cmd + K`: Quick search
- `Ctrl/Cmd + S`: Save (when editing)
- `Esc`: Close modal
- `?`: Show keyboard shortcuts

### CSV Import Formats

**Products**:
```csv
title,description,category_id,sku,unit_size,consumer_price,distributor_price,stock_quantity
"Organic Jaggery","Pure jaggery",1,"JAG-001","1kg",150,120,100
```

**Stock Update**:
```csv
sku,quantity_delta,notes
"JAG-001",50,"Restocked"
"MILK-001",-10,"Damaged units"
```

### API Access

For advanced users, API documentation is available at:
- Swagger UI: https://api.indostarnaturals.com/docs
- API Guide: See docs/API.md

### System Requirements

**Recommended Browser**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Internet Speed**:
- Minimum: 2 Mbps
- Recommended: 5+ Mbps

### Glossary

- **SKU**: Stock Keeping Unit - unique product identifier
- **Consumer Price**: Retail price for regular customers
- **Distributor Price**: Wholesale price for bulk buyers
- **Soft Delete**: Product hidden but data retained
- **Audit Log**: Record of all system changes
- **Webhook**: Automated notification from external service
