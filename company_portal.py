"""
회사 홈페이지
할일 목록을 관리한다.
할일을 추가 수정 삭제할 수 있는 기능을 제공한다.
FastAPI를 기반으로 개발한다. 
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# FastAPI 앱 초기화
app = FastAPI(
    title="Company Portal - Todo Management System",
    description="회사 홈페이지 - 할일 관리 시스템",
    version="1.0.0",
    docs_url="/doc",
    redoc_url="/redoc"
)

# ============ 데이터 모델 ============

class Todo(BaseModel):
    """할일 데이터 모델"""
    id: Optional[int] = None
    title: str
    description: str = ""
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TodoCreate(BaseModel):
    """할일 생성 요청"""
    title: str
    description: str = ""

class TodoUpdate(BaseModel):
    """할일 수정 요청"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# ============ 데이터 저장소 ============

todos_store: dict = {}  # {id: Todo}
next_id: int = 1

# ============ 유틸리티 함수 ============

def generate_id() -> int:
    """새로운 할일 ID 생성"""
    global next_id
    current_id = next_id
    next_id += 1
    return current_id

# ============ HTML 페이지 ============

def get_html_page():
    """웹 사이트 HTML 페이지"""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>회사 홈페이지 - 할일 관리 시스템</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                padding: 30px;
            }
            
            .input-section {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .input-group {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .input-group label {
                font-weight: 600;
                color: #333;
            }
            
            .input-group input,
            .input-group textarea {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-family: inherit;
                font-size: 1em;
                transition: border-color 0.3s;
                resize: vertical;
            }
            
            .input-group input:focus,
            .input-group textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .btn-add {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                align-self: flex-end;
                height: 44px;
            }
            
            .btn-add:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            
            .main-layout {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 30px;
                align-items: start;
            }
            
            .calendar-section {
                background: #f9f9f9;
                border-radius: 10px;
                padding: 20px;
                height: fit-content;
            }
            
            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .calendar-header h3 {
                color: #333;
                font-size: 1.2em;
            }
            
            .calendar-nav {
                display: flex;
                gap: 5px;
            }
            
            .calendar-nav button {
                background: #667eea;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9em;
            }
            
            .calendar-nav button:hover {
                background: #764ba2;
            }
            
            .calendar-month {
                text-align: center;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                font-size: 1.1em;
            }
            
            .calendar-weekdays {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 5px;
                margin-bottom: 10px;
            }
            
            .calendar-weekday {
                text-align: center;
                font-weight: 600;
                color: #667eea;
                font-size: 0.85em;
                padding: 5px;
            }
            
            .calendar-days {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 5px;
            }
            
            .calendar-day {
                aspect-ratio: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 0.85em;
                padding: 3px;
            }
            
            .calendar-day:hover {
                border-color: #667eea;
                background: #f0f0ff;
            }
            
            .calendar-day.other-month {
                color: #ccc;
                background: #fafafa;
            }
            
            .calendar-day.selected {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            
            .calendar-day-number {
                font-weight: 600;
            }
            
            .calendar-day-count {
                font-size: 0.7em;
                color: #999;
            }
            
            .calendar-day.selected .calendar-day-count {
                color: #ddd;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 3px 15px rgba(102, 126, 234, 0.2);
            }
            
            .stat-card .number {
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .stat-card .label {
                font-size: 0.95em;
                opacity: 0.9;
            }
            
            .todos-section {
                min-height: 400px;
            }
            
            .todos-section-title {
                font-size: 1.2em;
                font-weight: 600;
                color: #333;
                margin-bottom: 20px;
            }
            
            .todos-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .todo-item {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
                transition: all 0.2s;
                border-left: 4px solid #667eea;
                border: 1px solid #e0e0e0;
                border-left: 4px solid #667eea;
            }
            
            .todo-item:hover {
                box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            }
            
            .todo-item.completed {
                opacity: 0.6;
                border-left-color: #4caf50;
            }
            
            .todo-item.completed .todo-title {
                text-decoration: line-through;
                color: #999;
            }
            
            .todo-checkbox {
                width: 20px;
                height: 20px;
                cursor: pointer;
                accent-color: #667eea;
                margin-top: 2px;
                flex-shrink: 0;
            }
            
            .todo-content {
                flex: 1;
                min-width: 0;
            }
            
            .todo-title {
                font-weight: 600;
                color: #333;
                word-break: break-word;
                margin-bottom: 3px;
            }
            
            .todo-description {
                font-size: 0.9em;
                color: #666;
                word-break: break-word;
            }
            
            .todo-actions {
                display: flex;
                gap: 8px;
                flex-shrink: 0;
            }
            
            .btn-delete {
                background: #ff6b6b;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background 0.2s;
            }
            
            .btn-delete:hover {
                background: #ff5252;
            }
            
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #999;
            }
            
            .empty-state-icon {
                font-size: 4em;
                margin-bottom: 15px;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }

            @media (max-width: 768px) {
                .main-layout {
                    grid-template-columns: 1fr;
                }
                
                .input-section {
                    grid-template-columns: 1fr;
                }
                
                .stats {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 할일 관리 시스템</h1>
                <p>회사 홈페이지</p>
            </div>
            
            <div class="content">
                <!-- 입력 섹션 -->
                <div class="input-section">
                    <div class="input-group">
                        <label for="todoTitle">할일 제목</label>
                        <input type="text" id="todoTitle" placeholder="할일을 입력하세요">
                    </div>
                    <div class="input-group">
                        <label for="todoDescription">설명</label>
                        <textarea id="todoDescription" placeholder="상세 설명을 입력하세요" rows="1"></textarea>
                    </div>
                </div>
                
                <button class="btn-add" onclick="addTodo()">➕ 할일 추가</button>
                
                <!-- 통계 섹션 -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="number" id="totalCount">0</div>
                        <div class="label">전체 할일</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="completedCount">0</div>
                        <div class="label">완료</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="pendingCount">0</div>
                        <div class="label">미완료</div>
                    </div>
                </div>
                
                <!-- 메인 레이아웃: 달력 + 할일 목록 -->
                <div class="main-layout">
                    <!-- 달력 섹션 -->
                    <div class="calendar-section">
                        <div class="calendar-header">
                            <h3 id="calendarTitle">2024년 1월</h3>
                            <div class="calendar-nav">
                                <button onclick="previousMonth()">◀</button>
                                <button onclick="nextMonth()">▶</button>
                            </div>
                        </div>
                        
                        <div class="calendar-weekdays">
                            <div class="calendar-weekday">일</div>
                            <div class="calendar-weekday">월</div>
                            <div class="calendar-weekday">화</div>
                            <div class="calendar-weekday">수</div>
                            <div class="calendar-weekday">목</div>
                            <div class="calendar-weekday">금</div>
                            <div class="calendar-weekday">토</div>
                        </div>
                        
                        <div class="calendar-days" id="calendarDays"></div>
                    </div>
                    
                    <!-- 할일 목록 섹션 -->
                    <div class="todos-section">
                        <div class="todos-section-title">📋 할일 목록</div>
                        <div class="todos-list" id="todosList">
                            <div class="loading">할일을 불러오는 중...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const API_BASE = '/api';
            let currentDate = new Date();
            let selectedDate = null;
            let allTodos = [];
            
            // 달력 렌더링
            function renderCalendar() {
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                // 월 제목 업데이트
                const monthNames = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
                document.getElementById('calendarTitle').textContent = `${year}년 ${monthNames[month]}`;
                
                // 달력 일 계산
                const firstDay = new Date(year, month, 1).getDay();
                const lastDate = new Date(year, month + 1, 0).getDate();
                const prevLastDate = new Date(year, month, 0).getDate();
                
                let calendarDays = '';
                
                // 이전 달의 날짜
                for (let i = firstDay - 1; i >= 0; i--) {
                    calendarDays += `<div class="calendar-day other-month">${prevLastDate - i}</div>`;
                }
                
                // 현재 달의 날짜
                for (let date = 1; date <= lastDate; date++) {
                    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
                    const todosOnDate = allTodos.filter(todo => {
                        const todoDate = new Date(todo.created_at).toISOString().split('T')[0];
                        return todoDate === dateStr;
                    });
                    
                    const isSelected = selectedDate === dateStr;
                    const count = todosOnDate.length;
                    
                    calendarDays += `
                        <div class="calendar-day ${isSelected ? 'selected' : ''}" onclick="selectDate('${dateStr}')">
                            <div class="calendar-day-number">${date}</div>
                            ${count > 0 ? `<div class="calendar-day-count">${count}</div>` : ''}
                        </div>
                    `;
                }
                
                // 다음 달의 날짜
                const totalCells = firstDay + lastDate;
                const remainingCells = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
                for (let i = 1; i <= remainingCells; i++) {
                    calendarDays += `<div class="calendar-day other-month">${i}</div>`;
                }
                
                document.getElementById('calendarDays').innerHTML = calendarDays;
            }
            
            function previousMonth() {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar();
            }
            
            function nextMonth() {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar();
            }
            
            function selectDate(dateStr) {
                selectedDate = selectedDate === dateStr ? null : dateStr;
                renderCalendar();
                filterAndRenderTodos();
            }
            
            // 할일 추가
            async function addTodo() {
                const title = document.getElementById('todoTitle').value.trim();
                const description = document.getElementById('todoDescription').value.trim();
                
                if (!title) {
                    alert('할일 제목을 입력하세요.');
                    return;
                }
                
                try {
                    const response = await fetch(`${API_BASE}/todos`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            title: title,
                            description: description
                        })
                    });
                    
                    if (response.ok) {
                        document.getElementById('todoTitle').value = '';
                        document.getElementById('todoDescription').value = '';
                        loadTodos();
                    }
                } catch (error) {
                    console.error('Error adding todo:', error);
                    alert('할일 추가 중 오류가 발생했습니다.');
                }
            }
            
            // 할일 목록 로드
            async function loadTodos() {
                try {
                    const response = await fetch(`${API_BASE}/todos`);
                    allTodos = await response.json();
                    
                    filterAndRenderTodos();
                    updateStats(allTodos);
                    renderCalendar();
                } catch (error) {
                    console.error('Error loading todos:', error);
                }
            }
            
            // 날짜별 필터링 및 렌더링
            function filterAndRenderTodos() {
                let filteredTodos = allTodos;
                
                if (selectedDate) {
                    filteredTodos = allTodos.filter(todo => {
                        const todoDate = new Date(todo.created_at).toISOString().split('T')[0];
                        return todoDate === selectedDate;
                    });
                }
                
                renderTodos(filteredTodos);
            }
            
            // 할일 렌더링
            function renderTodos(todos) {
                const todosList = document.getElementById('todosList');
                
                if (todos.length === 0) {
                    const message = selectedDate 
                        ? `${selectedDate} 날짜에 할일이 없습니다.`
                        : '아직 할일이 없습니다. 새로운 할일을 추가해보세요!';
                    
                    todosList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">✨</div>
                            <p>${message}</p>
                        </div>
                    `;
                    return;
                }
                
                todosList.innerHTML = todos.map(todo => `
                    <div class="todo-item ${todo.completed ? 'completed' : ''}">
                        <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''} 
                               onchange="toggleTodo(${todo.id}, this.checked)">
                        <div class="todo-content">
                            <div class="todo-title">${escapeHtml(todo.title)}</div>
                            ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}
                        </div>
                        <div class="todo-actions">
                            <button class="btn-delete" onclick="deleteTodo(${todo.id})">🗑️</button>
                        </div>
                    </div>
                `).join('');
            }
            
            // 할일 완료 토글
            async function toggleTodo(todoId, completed) {
                try {
                    const response = await fetch(`${API_BASE}/todos/${todoId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            completed: completed
                        })
                    });
                    
                    if (response.ok) {
                        loadTodos();
                    }
                } catch (error) {
                    console.error('Error updating todo:', error);
                }
            }
            
            // 할일 삭제
            async function deleteTodo(todoId) {
                if (!confirm('이 할일을 삭제하시겠습니까?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`${API_BASE}/todos/${todoId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        loadTodos();
                    }
                } catch (error) {
                    console.error('Error deleting todo:', error);
                    alert('할일 삭제 중 오류가 발생했습니다.');
                }
            }
            
            // 통계 업데이트
            function updateStats(todos) {
                const total = todos.length;
                const completed = todos.filter(t => t.completed).length;
                const pending = total - completed;
                
                document.getElementById('totalCount').textContent = total;
                document.getElementById('completedCount').textContent = completed;
                document.getElementById('pendingCount').textContent = pending;
            }
            
            // HTML 이스케이프
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Enter 키로 추가
            document.getElementById('todoTitle').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    addTodo();
                }
            });
            
            document.getElementById('todoDescription').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    addTodo();
                }
            });
            
            // 초기 로드
            loadTodos();
        </script>
    </body>
    </html>
    """

# ============ API 엔드포인트 ============

@app.get("/", response_class=HTMLResponse)
async def root():
    """웹사이트 홈페이지"""
    return get_html_page()

# -------- 할일 추가 --------
@app.post("/api/todos", response_model=Todo, status_code=201)
async def add_todo(todo_create: TodoCreate):
    """
    새로운 할일을 추가한다.
    """
    todo_id = generate_id()
    now = datetime.now()
    
    todo = Todo(
        id=todo_id,
        title=todo_create.title,
        description=todo_create.description,
        completed=False,
        created_at=now,
        updated_at=now
    )
    
    todos_store[todo_id] = todo
    return todo

# -------- 할일 수정 --------
@app.put("/api/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """
    기존 할일을 수정한다.
    """
    if todo_id not in todos_store:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    
    existing_todo = todos_store[todo_id]
    
    # 필드 업데이트
    if todo_update.title is not None:
        existing_todo.title = todo_update.title
    if todo_update.description is not None:
        existing_todo.description = todo_update.description
    if todo_update.completed is not None:
        existing_todo.completed = todo_update.completed
    
    existing_todo.updated_at = datetime.now()
    todos_store[todo_id] = existing_todo
    
    return existing_todo

# -------- 할일 삭제 --------
@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int):
    """
    할일을 삭제한다.
    """
    if todo_id not in todos_store:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    
    del todos_store[todo_id]
    return None

# -------- 할일 조회 --------
@app.get("/api/todos", response_model=List[Todo])
async def get_todos():
    """
    모든 할일을 조회한다.
    """
    return list(todos_store.values())

@app.get("/api/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    """
    특정 할일을 조회한다.
    """
    if todo_id not in todos_store:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    
    return todos_store[todo_id]

# ============ 실행 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)