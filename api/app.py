"""
Mini ERPNext - Flask Web API
Provides RESTful API access to the ERP system.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS
import core.frappe as frappe
from core.database import db, get_table_name

app = Flask(__name__)
CORS(app)


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker"""
    return jsonify({
        "status": "healthy",
        "service": "Mini ERPNext API",
        "version": "1.0.0"
    })


# ==================== GENERIC CRUD ====================

@app.route('/api/<doctype>', methods=['GET'])
def list_documents(doctype):
    """List all documents of a doctype"""
    try:
        # Convert URL-friendly name to doctype
        dt = doctype.replace('-', ' ').title()
        table = get_table_name(dt)
        
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        data = db.sql(f"SELECT * FROM {table} LIMIT ? OFFSET ?", (limit, offset), as_dict=True)
        
        return jsonify({
            "doctype": dt,
            "data": data,
            "count": len(data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/<doctype>/<name>', methods=['GET'])
def get_document(doctype, name):
    """Get a single document by name"""
    try:
        dt = doctype.replace('-', ' ').title()
        doc = frappe.get_doc(dt, name)
        
        return jsonify({
            "doctype": dt,
            "name": name,
            "data": doc.as_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/<doctype>', methods=['POST'])
def create_document(doctype):
    """Create a new document"""
    try:
        dt = doctype.replace('-', ' ').title()
        data = request.get_json()
        
        doc = frappe.get_doc(dt, **data)
        doc.save()
        
        return jsonify({
            "doctype": dt,
            "name": doc.name,
            "message": "Created successfully",
            "data": doc.as_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/<doctype>/<name>', methods=['PUT'])
def update_document(doctype, name):
    """Update an existing document"""
    try:
        dt = doctype.replace('-', ' ').title()
        data = request.get_json()
        
        doc = frappe.get_doc(dt, name)
        for key, value in data.items():
            doc._data[key] = value
        doc.save()
        
        return jsonify({
            "doctype": dt,
            "name": doc.name,
            "message": "Updated successfully",
            "data": doc.as_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/<doctype>/<name>', methods=['DELETE'])
def delete_document(doctype, name):
    """Delete a document"""
    try:
        dt = doctype.replace('-', ' ').title()
        table = get_table_name(dt)
        
        db.sql(f"DELETE FROM {table} WHERE name = ?", (name,))
        db.commit()
        
        return jsonify({
            "doctype": dt,
            "name": name,
            "message": "Deleted successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==================== WORKFLOW ACTIONS ====================

@app.route('/api/<doctype>/<name>/submit', methods=['POST'])
def submit_document(doctype, name):
    """Submit a document (change docstatus to 1)"""
    try:
        dt = doctype.replace('-', ' ').title()
        doc = frappe.get_doc(dt, name)
        doc.submit()
        
        return jsonify({
            "doctype": dt,
            "name": doc.name,
            "message": "Submitted successfully",
            "docstatus": 1
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/<doctype>/<name>/cancel', methods=['POST'])
def cancel_document(doctype, name):
    """Cancel a submitted document"""
    try:
        dt = doctype.replace('-', ' ').title()
        doc = frappe.get_doc(dt, name)
        doc.cancel()
        
        return jsonify({
            "doctype": dt,
            "name": doc.name,
            "message": "Cancelled successfully",
            "docstatus": 2
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==================== REPORTS ====================

@app.route('/api/report/stock-balance', methods=['GET'])
def stock_balance_report():
    """Get stock balance from Bin table"""
    try:
        table = get_table_name("Bin")
        data = db.sql(f"SELECT item_code, warehouse, actual_qty, reserved_qty FROM {table}", as_dict=True)
        
        return jsonify({
            "report": "Stock Balance",
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/report/sales-summary', methods=['GET'])
def sales_summary_report():
    """Get sales order summary"""
    try:
        table = get_table_name("Sales Order")
        data = db.sql(f"""
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN docstatus = 0 THEN 1 ELSE 0 END) as draft,
                SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) as submitted,
                SUM(CASE WHEN docstatus = 2 THEN 1 ELSE 0 END) as cancelled,
                SUM(grand_total) as total_value
            FROM {table}
        """, as_dict=True)
        
        return jsonify({
            "report": "Sales Summary",
            "data": data[0] if data else {}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== ENTRY POINT ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
