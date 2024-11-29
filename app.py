from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(10), default='Pending')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        data = request.get_json()
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created!'}), 201

    status = request.args.get('status')
    if status:
        tasks = Task.query.filter_by(status=status).all()
    else:
        tasks = Task.query.all()

    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat(),
        'status': task.status
    } for task in tasks])

@app.route('/tasks/<int:id>', methods=['PUT'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    task.title = data['title']
    task.description = data.get('description', task.description)
    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.status = data.get('status', task.status)
    
    db.session.commit()
    return jsonify({'message': 'Task updated!'}), 200

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted!'}), 204

@app.route('/tasks/<int:id>/status', methods=['PATCH'])
def toggle_task_status(id):
    task = Task.query.get_or_404(id)
    task.status = 'Completed' if task.status == 'Pending' else 'Pending'
    db.session.commit()
    return jsonify({'message': f'Task status updated to {task.status}'}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)