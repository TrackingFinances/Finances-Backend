from decimal import Decimal
from flask import Flask,request,jsonify
from sqlalchemy import func
from config import Config
from models import Income, Investment, db,Expense,User,Currency
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_required,login_user,logout_user
from customExceptions import InternalServerException
from flask_migrate import Migrate
from datetime import datetime

app= Flask(__name__)
CORS(app,supports_credentials=True)
app.config.from_object(Config)

db.init_app(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
migrate = Migrate(app,db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def usernameExists(username):
    if User.query.filter_by(name=username).first():
        return True
    else :
        return False

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error':'No data is provided'}),400

        name=data.get('username')
        plaintext=data.get('plaintext')
        
        if usernameExists(name) :
            return jsonify({'error':'Username already exists'}),400
        
        newUser = User(name=name)
        newUser.setHashText(plainText=plaintext)
        db.session.add(newUser)
        db.session.commit()
        return jsonify({'message':'User is added'}),201
            
    except InternalServerException as e:
        return jsonify({'error':str(e)}),500
    
    
# Create User Login Route
@app.route('/login', methods=['GET'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        plainText = data.get('password')

        user = User.query.filter_by(name=username).first()
        if user and user.checkPlainText(plainText):
            if login_user(user) :
                return jsonify({"message": "Logged in successfully."}), 200
            return jsonify({"message": "Invalid username or password."}), 401
        return jsonify({'error':'Failed login as user is inactive'}),403
    except InternalServerException as e:
        return jsonify({'error':str(e)}),500


# Create User Logout Route
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."}), 200

@app.route('/currentUser', methods=['GET'])
@login_required
def get_current_user():
    """Fetches the current user details."""
    
    user = {
        'id': str(current_user.id),
        'username': current_user.name,

    }
    return jsonify(user), 200

@app.route('/addExpense',methods=['POST'])
@login_required
def addExpense():

    data = request.get_json()

    if data is None:
        return jsonify({'error':'No data is provided'}),400
    

    user_id=data.get('user')
    amount=data.get('amount')
    currency=data.get('currency')
    date=data.get('date')

    if user_id is None :
        return jsonify({'error':'User not found'}),404
    if User.query.filter_by(id=user_id).first() is None:
        return jsonify({'error':'User not found'}),404
    if amount is None:
        amount=0
    if currency is None:
        return jsonify({'error':'Currency is required'}),400
    if Currency.query.filter_by(currency=currency).first() is None:
        return jsonify({'error': 'Selected currency not available'}),500
    if date:
        try:
            date=datetime.fromisoformat(date)
            print(date)
        except ValueError:
            return jsonify({'error':'Invalid date format'}),400
    else :
        return jsonify({'error':'Date of expense is required'}),400

    expense= Expense(user_id=user_id,amount=Decimal(amount),currency=currency,date=date)

    db.session.add(expense)
    db.session.commit()
    return jsonify({'message':'Expense added'}),201

@app.route('/getExpense',methods=['GET'])
@login_required
def getExpense():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error':'No data is provided'}),400
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if user_id is None :
            return jsonify({'error':'User not found'}),404
        
        if start_date is None or end_date is None:
            return jsonify({'error': 'Start date and end date are required.'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return jsonify({'error':'Datetime format is wrong'}),400
        
        total_expense = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id==user_id,
            Expense.date>=start_date,
            Expense.date<=end_date
            ).scalar()
        
        if total_expense is None:
            total_expense = 0
        return jsonify({'user_id':user_id,'total_expense':float(total_expense)}),200
        

    except InternalServerException:
        return jsonify({'error':'Internal server error'}),500

@app.route('/addIncome',methods=['POST'])
@login_required
def addIncome():

    data = request.get_json()

    if data is None:
        return jsonify({'error':'No data is provided'}),400
    

    user_id=data.get('user')
    amount=data.get('amount')
    currency=data.get('currency')
    date=data.get('date')

    if user_id is None :
        return jsonify({'error':'User not found'}),404
    if User.query.filter_by(id=user_id).first() is None:
        return jsonify({'error':'User not found'}),404
    if amount is None:
        amount=0
    if currency is None:
        return jsonify({'error':'Currency is required'}),400
    if Currency.query.filter_by(currency=currency).first() is None:
        return jsonify({'error': 'Selected currency not available'}),500
    if date:
        try:
            date=datetime.fromisoformat(date)
            print(date)
        except ValueError:
            return jsonify({'error':'Invalid date format'}),400
    else :
        return jsonify({'error':'Date of income is required'}),400

    income= Income(user_id=user_id,amount=Decimal(amount),currency=currency,date=date)

    db.session.add(income)
    db.session.commit()
    return jsonify({'message':'Income added'}),201

@app.route('/getIncome',methods=['GET'])
@login_required
def getIncome():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error':'No data is provided'}),400
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if user_id is None :
            return jsonify({'error':'User not found'}),404
        
        if start_date is None or end_date is None:
            return jsonify({'error': 'Start date and end date are required.'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return jsonify({'error':'Datetime format is wrong'}),400
        
        total_income = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id==user_id,
            Income.date>=start_date,
            Income.date<=end_date
            ).scalar()
        
        if total_income is None:
            total_income = 0
        return jsonify({'user_id':user_id,'total_income':float(total_income)}),200
        

    except InternalServerException:
        return jsonify({'error':'Internal server error'}),500

@app.route('/addInvestment',methods=['POST'])
@login_required
def addInvestment():

    data = request.get_json()

    if data is None:
        return jsonify({'error':'No data is provided'}),400
    

    user_id=data.get('user')
    amount=data.get('amount')
    currency=data.get('currency')
    date=data.get('date')

    if user_id is None :
        return jsonify({'error':'User not found'}),404
    if User.query.filter_by(id=user_id).first() is None:
        return jsonify({'error':'User not found'}),404
    if amount is None:
        amount=0
    if currency is None:
        return jsonify({'error':'Currency is required'}),400
    if Currency.query.filter_by(currency=currency).first() is None:
        return jsonify({'error': 'Selected currency not available'}),500
    if date:
        try:
            date=datetime.fromisoformat(date)
            print(date)
        except ValueError:
            return jsonify({'error':'Invalid date format'}),400
    else :
        return jsonify({'error':'Date of investment is required'}),400

    investment = Investment(user_id=user_id,amount=Decimal(amount),currency=currency,date=date)

    db.session.add(investment)
    db.session.commit()
    return jsonify({'message':'Investment added'}),201

@app.route('/getInvestment',methods=['GET'])
@login_required
def getInvestment():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error':'No data is provided'}),400
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if user_id is None :
            return jsonify({'error':'User not found'}),404
        
        if start_date is None or end_date is None:
            return jsonify({'error': 'Start date and end date are required.'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return jsonify({'error':'Datetime format is wrong'}),400
        
        total_investment = db.session.query(db.func.sum(Investment.amount)).filter(
            Investment.user_id==user_id,
            Investment.date>=start_date,
            Investment.date<=end_date
            ).scalar()
        
        if total_investment is None:
            total_investment = 0
        return jsonify({'user_id':user_id,'total_investment':float(total_investment)}),200
        

    except InternalServerException:
        return jsonify({'error':'Internal server error'}),500

@app.route('/getAll', methods=['GET'])
@login_required
def get_all():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error':'No data is provided'}),400
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')


        
        if user_id is None :
            return jsonify({'error':'User not found'}),404
        
        if start_date is None or end_date is None:
            return jsonify({'error': 'Start date and end date are required.'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return jsonify({'error':'Datetime format is wrong'}),400

        
        expenses_query = db.session.query(
            Expense.date,
            Expense.amount,
            Expense.currency,
            db.literal('expense').label('transactionType')
            ).filter(
                Expense.user_id==user_id,
                Expense.date>=start_date,
                Expense.date<=end_date
            )
        
        incomes_query = db.session.query(
            Income.date,
            Income.amount,
            Income.currency,
            db.literal('income').label('transactionType')
            ).filter(
                Income.user_id==user_id,
                Income.date>=start_date,
                Income.date<=end_date
            )
        
        investment_query = db.session.query(
            Investment.date,
            Investment.amount,
            Investment.currency,
            db.literal('investment').label('transactionType')
            ).filter(
                Investment.user_id==user_id,
                Investment.date>=start_date,
                Investment.date<=end_date
        )

        combined_queries = expenses_query.union(incomes_query).union(investment_query).order_by(Expense.date)
        result= combined_queries.all()

        finances_data=[]
        for row in result:
            finances_data.append({
                'date':row.date.isoformat(),
                'amount':float(row.amount),
                'currency':row.currency,
                'transactionType':row.transactionType
            })
        return jsonify(finances_data),200

    except InternalServerException:
        return jsonify({'error':'Internal server error'}),500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)