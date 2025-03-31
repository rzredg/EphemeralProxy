from flask import Flask, request, jsonify
import jwt
import datetime
import os
import secrets

app = Flask(__name__)

# In production, use a proper secure storage method
# This is just for demonstration
TOKENS = {}
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))

def generate_token(user_id, expires_in_hours=24):
    """Generate a new token for a user."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    # Store token in our simple database (in production, use Redis or similar)
    TOKENS[token] = {
        'user_id': user_id,
        'expires': expiration,
        'created': datetime.datetime.utcnow()
    }
    return token

@app.route('/validate_token', methods=['GET'])
def validate_token():
    """Validate a token from the Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    
    # Check if the header is properly formatted
    if not auth_header.startswith('Bearer '):
        return '', 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verify the token signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # Check if token is in our database (could be revoked)
        if token not in TOKENS:
            return '', 401
            
        # Token is valid
        return '', 200
        
    except jwt.ExpiredSignatureError:
        # Token has expired
        if token in TOKENS:
            del TOKENS[token]  # Clean up expired token
        return '', 401
        
    except jwt.InvalidTokenError:
        # Token is invalid
        return '', 401

@app.route('/generate_token', methods=['POST'])
def create_token():
    """Generate a new token (protected by separate authentication)."""
    # In a real system, this endpoint would be protected
    # and only accessible to authorized administrators
    user_id = request.json.get('user_id')
    hours = request.json.get('hours', 24)
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
        
    token = generate_token(user_id, hours)
    return jsonify({
        'token': token,
        'expires_in_hours': hours,
        'created': datetime.datetime.utcnow().isoformat()
    })

@app.route('/list_tokens', methods=['GET'])
def list_tokens():
    """List all active tokens (admin only in production)."""
    tokens_info = []
    for token, info in TOKENS.items():
        tokens_info.append({
            'token_preview': token[:10] + '...',
            'user_id': info['user_id'],
            'expires': info['expires'].isoformat(),
            'created': info['created'].isoformat()
        })
    return jsonify(tokens_info)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888)
