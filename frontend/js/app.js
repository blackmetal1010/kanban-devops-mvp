/**
 * Main Kanban application logic.
 * Requires auth.js and api.js to be loaded first.
 */
const App = (() => {
  let currentProjectId = null;
  let tasks = [];
  let draggingTaskId = null;

  // ── Bootstrap ──────────────────────────────────────────────
  async function init() {
    if (!Auth.isLoggedIn()) {
      window.location.href = 'login.html';
      return;
    }

    const user = Auth.getUser();
    if (user) {
      document.getElementById('user-greeting').textContent = `👋 ${user.username}`;
    }

    await loadProjects();

    document.getElementById('project-select').addEventListener('change', (e) => {
      const pid = parseInt(e.target.value, 10);
      if (pid) selectProject(pid);
      else clearBoard();
    });

    document.getElementById('task-form').addEventListener('submit', onTaskFormSubmit);
  }

  // ── Projects ───────────────────────────────────────────────
  async function loadProjects() {
    let projects = [];
    try {
      projects = await API.get('/api/projects/');
    } catch (err) {
      showToast('Could not load projects: ' + err.message, 'error');
    }

    const select = document.getElementById('project-select');
    const current = select.value;
    select.innerHTML = '<option value="">— Select a project —</option>';
    projects.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      select.appendChild(opt);
    });

    if (current && projects.find((p) => p.id === parseInt(current, 10))) {
      select.value = current;
    }
  }

  async function selectProject(projectId) {
    currentProjectId = projectId;
    document.getElementById('board-empty').classList.add('hidden');
    document.getElementById('board-columns').classList.remove('hidden');
    await loadTasks();
  }

  function clearBoard() {
    currentProjectId = null;
    tasks = [];
    document.getElementById('board-empty').classList.remove('hidden');
    document.getElementById('board-columns').classList.add('hidden');
    renderBoard();
  }

  // ── Tasks ──────────────────────────────────────────────────
  async function loadTasks() {
    if (!currentProjectId) return;
    try {
      tasks = await API.get(`/api/tasks/?project_id=${currentProjectId}`);
    } catch (err) {
      showToast('Could not load tasks: ' + err.message, 'error');
      tasks = [];
    }
    renderBoard();
  }

  function renderBoard() {
    const statuses = ['todo', 'in_progress', 'done'];
    statuses.forEach((status) => {
      const list = document.getElementById(`tasks-${status}`);
      const count = document.getElementById(`count-${status}`);
      const statusTasks = tasks.filter((t) => t.status === status);
      list.innerHTML = '';
      statusTasks.forEach((task) => list.appendChild(createTaskCard(task)));
      count.textContent = statusTasks.length;
    });
  }

  function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.setAttribute('draggable', 'true');
    card.setAttribute('data-task-id', task.id);
    card.setAttribute('data-priority', task.priority);

    // Due date formatting
    let dueDateHtml = '';
    if (task.due_date) {
      const due = new Date(task.due_date);
      const isOverdue = due < new Date() && task.status !== 'done';
      const dateStr = due.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      dueDateHtml = `<span class="due-date ${isOverdue ? 'overdue' : ''}">📅 ${dateStr}</span>`;
    }

    card.innerHTML = `
      <div class="task-card-actions">
        <button class="task-edit-btn" onclick="App.openTaskModal(${task.id})">Edit</button>
      </div>
      <div class="task-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
      <div class="task-meta">
        <span class="priority-badge priority-${task.priority}">${task.priority}</span>
        ${dueDateHtml}
      </div>
    `;

    card.addEventListener('dragstart', (e) => {
      draggingTaskId = task.id;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', task.id);
    });
    card.addEventListener('dragend', () => card.classList.remove('dragging'));

    return card;
  }

  // ── Drag & Drop ────────────────────────────────────────────
  async function handleDrop(event) {
    event.preventDefault();
    const column = event.currentTarget;
    const newStatus = column.getAttribute('data-status');
    column.classList.remove('drag-over');

    if (!draggingTaskId) return;

    const task = tasks.find((t) => t.id === draggingTaskId);
    if (!task || task.status === newStatus) return;

    // Optimistic update
    task.status = newStatus;
    renderBoard();

    try {
      await API.put(`/api/tasks/${draggingTaskId}`, { status: newStatus });
    } catch (err) {
      showToast('Failed to update task: ' + err.message, 'error');
      await loadTasks();
    }
    draggingTaskId = null;
  }

  // Column drag-over highlighting
  document.querySelectorAll && document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.column').forEach((col) => {
      col.addEventListener('dragover', (e) => { e.preventDefault(); col.classList.add('drag-over'); });
      col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
      col.addEventListener('drop', () => col.classList.remove('drag-over'));
    });
  });

  // ── Task Modal ─────────────────────────────────────────────
  function openTaskModal(taskId = null, defaultStatus = 'todo') {
    const form = document.getElementById('task-form');
    form.reset();
    document.getElementById('task-id').value = '';

    const deleteBtn = document.getElementById('delete-task-btn');
    const modalTitle = document.getElementById('modal-title');

    if (taskId) {
      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;
      modalTitle.textContent = 'Edit Task';
      document.getElementById('task-id').value = task.id;
      document.getElementById('task-title').value = task.title;
      document.getElementById('task-description').value = task.description || '';
      document.getElementById('task-status').value = task.status;
      document.getElementById('task-priority').value = task.priority;
      if (task.due_date) {
        // datetime-local expects "YYYY-MM-DDTHH:MM"
        document.getElementById('task-due-date').value = task.due_date.slice(0, 16);
      }
      deleteBtn.classList.remove('hidden');
    } else {
      modalTitle.textContent = 'New Task';
      document.getElementById('task-status').value = defaultStatus;
      deleteBtn.classList.add('hidden');
    }

    document.getElementById('task-modal-overlay').classList.remove('hidden');
    document.getElementById('task-title').focus();
  }

  function closeTaskModal() {
    document.getElementById('task-modal-overlay').classList.add('hidden');
  }

  async function onTaskFormSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('save-task-btn');
    btn.disabled = true;

    const taskId = document.getElementById('task-id').value;
    const payload = {
      title: document.getElementById('task-title').value.trim(),
      description: document.getElementById('task-description').value.trim() || null,
      status: document.getElementById('task-status').value,
      priority: document.getElementById('task-priority').value,
      due_date: document.getElementById('task-due-date').value || null,
    };

    try {
      if (taskId) {
        const updated = await API.put(`/api/tasks/${taskId}`, payload);
        const idx = tasks.findIndex((t) => t.id === parseInt(taskId, 10));
        if (idx !== -1) tasks[idx] = updated;
      } else {
        payload.project_id = currentProjectId;
        const created = await API.post('/api/tasks/', payload);
        tasks.push(created);
      }
      renderBoard();
      closeTaskModal();
      showToast(taskId ? 'Task updated!' : 'Task created!');
    } catch (err) {
      showToast(err.message || 'Failed to save task', 'error');
    } finally {
      btn.disabled = false;
    }
  }

  async function deleteCurrentTask() {
    const taskId = document.getElementById('task-id').value;
    if (!taskId) return;
    if (!confirm('Delete this task?')) return;
    try {
      await API.delete(`/api/tasks/${taskId}`);
      tasks = tasks.filter((t) => t.id !== parseInt(taskId, 10));
      renderBoard();
      closeTaskModal();
      showToast('Task deleted.');
    } catch (err) {
      showToast(err.message || 'Failed to delete task', 'error');
    }
  }

  // ── Toast ──────────────────────────────────────────────────
  let toastTimer = null;
  function showToast(msg, type = '') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = `toast${type ? ' ' + type : ''}`;
    toast.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.add('hidden'), 3000);
  }

  // ── Utilities ──────────────────────────────────────────────
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ── Auto-init ──────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return {
    loadProjects,
    selectProject,
    openTaskModal,
    closeTaskModal,
    deleteCurrentTask,
    handleDrop,
    showToast,
  };
})();
