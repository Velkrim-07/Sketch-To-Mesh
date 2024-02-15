import bcrypt

def hash_password(password):
    
    #password_bytes = password.encode('utf-8')
    # Generate a salt and hash a password
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    
    return hashed_password

def check_credentials(hashed_password_input, hashed_password_db):
    is_valid = bcrypt.checkpw(hashed_password_input, hashed_password_db)
    return is_valid
