from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# Example hash
hashed_password = bcrypt.generate_password_hash("123456").decode('utf-8')
print(hashed_password)
