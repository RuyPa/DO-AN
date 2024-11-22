



import flask_bcrypt

password = '123456'
password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')
print( flask_bcrypt.check_password_hash(password_hash, password))
print(password_hash)
