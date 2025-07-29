from companies.views.base import Base
from companies.utils.permissions import TaskPermission
from companies.serializer import TaskSerializer, TasksSerializer
from companies.models import Task

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

import datetime

class Tasks(Base, APIView):
    permission_classes = [TaskPermission]

    def get(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)

        tasks = Task.objects.filter(enterprise_id=enterprise_id).all() #Pegar todas as tarefas de uma empresa
        

        serializer = TasksSerializer(tasks, many=True)

        return Response({"task":serializer.data})
    
    def post(self, request):
        employee_id = request.data.get('employee_id')
        title = request.data.get('title')
        description = request.data.get('description')
        status_id = request.data.get('status_id')
        due_date = request.data.get('due_date')

        # Validar se employee_id foi fornecido
        if not employee_id:
            raise APIException("O ID do funcionário é obrigatório.")

        employee = self.get_employee(employee_id, request.user.id)
        
        # Validar se status_id foi fornecido
        if not status_id:
            raise APIException("O ID do status é obrigatório.")
            
        _status = self.get_status(status_id)

        #Validators
        if not title:
            raise APIException("O título é obrigatório.")
            
        if len(title) > 125:
            raise APIException("O título deve ter no máximo 125 caracteres.")

        if due_date:    
            try:
                due_date = datetime.datetime.strptime(due_date,"%d/%m/%Y %H:%M")
            except ValueError:
                raise APIException("A data deve ter o padrão: d/m/Y H:M","date_invalid")
        
        try:
            task = Task.objects.create(
                title=title,
                description=description,
                due_date=due_date,
                employee_id=employee_id,
                enterprise_id=employee.enterprise.id,
                status_id=status_id,
            )
        except Exception as e:
            raise APIException(f"Erro ao criar a tarefa: {str(e)}")

        serializer = TaskSerializer(task)
        
        if not serializer.data:
            raise APIException("Erro ao serializar a tarefa criada.")

        return Response({"task":serializer.data})

class TaskDetail(Base):
    permission_classes = [TaskPermission]

    def get(self, request, task_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        task = self.get_task(task_id, enterprise_id)

        serializer = TaskSerializer(task)

        return Response({"task":serializer.data})

    def put(self, request, task_id):
        enterprise_id = self.get_enterprise_id(request.user.id)
        task = self.get_task(task_id, enterprise_id)

        title = request.data.get('title', task.title)
        employee_id = request.data.get('employee_id', task.employee.id)
        description = request.data.get('description', task.description)
        status_id = request.data.get('status_id', task.status.id)
        due_date = request.data.get('due_date', task.due_date)

        #Validators

        self.get_status(status_id)
        self.get_employee(employee_id, request.user.id)

        if due_date and due_date != task.due_date:    
            try:
                due_date = datetime.datetime.strptime(due_date,"%d/%m/%Y %H:%M")
            except ValueError:
                raise APIException("A data deve ter o padrão: d/m/Y H:M","date_invalid")

        data = {
            "title":title,
            "description":description,
            "due_date":due_date
        }

        serializer = TaskSerializer(task, data=data, partial=True)

        if not serializer.is_valid():
            raise APIException("Não foi possível editar a taréfa.")
    
        serializer.update(task, serializer.validated_data)

        task.status_id = status_id
        task.employee_id = employee_id
        task.save()

        return Response({"task":serializer.data})
    
    def delete(self, request, task_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        task = self.get_task(task_id, enterprise_id).delete()

        return Response({"success":True})
    
    

