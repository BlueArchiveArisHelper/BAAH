def enable_task_drag(task_list, on_move):
    """用原生拖放调整任务位置，仅在放下时把新位置传给配置页。"""
    task_list.on('dragstart', js_handler='''event => {
        const handle = event.target.closest('.baah-task-drag-handle');
        if (!handle) return;
        const list = event.currentTarget;
        const row = handle.closest('[data-task-index]');
        const rows = [...list.querySelectorAll('[data-task-index]')];
        const from = Number(row.dataset.taskIndex);
        const clearMarker = () => rows.forEach(item =>
            item.classList.remove('baah-task-drop-before', 'baah-task-drop-after'));
        list._baahTaskDrag = {
            from, to: from, rows, clearMarker,
            finish: () => {
                clearMarker();
                row.classList.remove('baah-task-dragging');
                delete list._baahTaskDrag;
            },
        };
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', String(from));
        const rect = row.getBoundingClientRect();
        event.dataTransfer.setDragImage(row, event.clientX - rect.left, event.clientY - rect.top);
        row.classList.add('baah-task-dragging');
    }''')
    update_marker = '''event => {
        const drag = event.currentTarget._baahTaskDrag;
        if (!drag) return;
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        const next = drag.rows.find(row => {
            const rect = row.getBoundingClientRect();
            return event.clientY < rect.top + rect.height / 2;
        });
        const insertion = next ? Number(next.dataset.taskIndex) : drag.rows.length;
        drag.to = insertion > drag.from ? insertion - 1 : insertion;
        drag.clearMarker();
        if (drag.to === drag.from) return;
        if (next) next.classList.add('baah-task-drop-before');
        else drag.rows[drag.rows.length - 1].classList.add('baah-task-drop-after');
    }'''
    task_list.on('dragenter', js_handler=update_marker)
    task_list.on('dragover', js_handler=update_marker)
    task_list.on('dragleave', js_handler='''event => {
        const list = event.currentTarget;
        if (list.contains(event.relatedTarget)) return;
        const drag = list._baahTaskDrag;
        if (drag) {
            drag.clearMarker();
            drag.to = drag.from;
        }
    }''')
    task_list.on('dragend', js_handler='''event => {
        event.currentTarget._baahTaskDrag?.finish();
    }''')
    task_list.on('drop', lambda event: on_move(event.args['from'], event.args['to']),
                 js_handler='''event => {
        const drag = event.currentTarget._baahTaskDrag;
        if (!drag) return;
        event.preventDefault();
        drag.finish();
        if (drag.from !== drag.to) emit({from: drag.from, to: drag.to});
    }''')
