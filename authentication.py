from .db_operations import insert_user, delete_user, get_user_by_email
from .bcrypt_password import check_credentials

def login_account(username, byte_password):
    
    user = get_user_by_email(username)
    
    if user:
    # if the credentials match, return login successful. == 1
        if user[0]['username'] == username and check_credentials(byte_password, user[0]['hashPassword']):
            print('LOG-authentication/login_account: Login Successful.')
            result = 1
            return user, result
        else:
            print('LOG-authentication/login_account: Login Failed; Credentials are incorrect.')
            result = 0
            user.clear()
            return user, result
    else:
        # User doesn't exist
        print("LOG-authentication/login_account: User not found. Please register.")
        result = -1
        return result
    
def register_account(username, hashed_password):
    
    # 0 == already in db
    # 1 == created successfully
    # -1 == other error.
    result = insert_user(username, hashed_password) # if fails (email has to be unique), just try to login
    
    if result == 0: # 0 is account already in DB. try to login then
        print("LOG-authentication/register_account: Account already exists. Redirecting to login_account")
    if result == 1:
        print("LOG-authentication/register_account: Created User Document successfully.")
    if result == -1:
        print("LOG-authentication/register_account: Error. Check console for more information.")
        
    return result
    
    