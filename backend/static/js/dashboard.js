const API_BASE = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
});

async function loadAllData() {
    try {
        await Promise.all([
            loadDashboardStats(),
            loadSystemHealth(),
            loadChannels(),
            loadAIRouting()
        ]);
    } catch (error) {
        showError('Ошибка загрузки данных: ' + error.message);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch(API_BASE + '/dashboard/stats');
        const stats = await response.json();
        
        const container = document.getElementById('stats-container');
        container.innerHTML = 
            '<div class="stat-card"><h3>📰 Новости за сутки</h3><div class="value">' + stats.news_found + '</div><div class="trend">Выбрано: ' + stats.news_selected + '</div></div>' +
            '<div class="stat-card"><h3>✍️ Постов создано</h3><div class="value">' + stats.posts_created + '</div><div class="trend">Опубликовано: ' + stats.posts_published + '</div></div>' +
            '<div class="stat-card"><h3>📊 Средний Quality Score</h3><div class="value">' + (stats.avg_quality_score || 0) + '</div><div class="trend">из 100</div></div>' +
            '<div class="stat-card"><h3>✅ Средний Fact Score</h3><div class="value">' + (stats.avg_fact_score || 0) + '</div><div class="trend">из 100</div></div>' +
            '<div class="stat-card"><h3>️ Общие просмотры</h3><div class="value">' + stats.total_views.toLocaleString() + '</div><div class="trend">ER: ' + stats.total_er + '%</div></div>' +
            '<div class="stat-card"><h3>⏳ Ожидают проверки</h3><div class="value">' + stats.drafts_pending + '</div><div class="trend">Ошибок: ' + stats.errors_count + '</div></div>';
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

async function loadSystemHealth() {
    try {
        const response = await fetch(API_BASE + '/dashboard/health');
        const health = await response.json();
        
        const container = document.getElementById('health-container');
        let healthHTML = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">';
        
        for (const [name, service] of Object.entries(health.services)) {
            const statusClass = service.status === 'OK' ? 'status-online' : 'status-offline';
            healthHTML += '<div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">';
            healthHTML += '<div style="font-weight: 600; margin-bottom: 5px;">' + name + '</div>';
            healthHTML += '<span class="status-badge ' + statusClass + '">' + service.status + '</span>';
            if (service.latency_ms) {
                healthHTML += '<div style="font-size: 12px; margin-top: 5px; color: rgba(255,255,255,0.7);">' + service.latency_ms + 'ms</div>';
            }
            healthHTML += '</div>';
        }
        
        healthHTML += '</div>';
        container.innerHTML = healthHTML;
    } catch (error) {
        console.error('Ошибка загрузки health:', error);
    }
}

async function loadChannels() {
    try {
        const response = await fetch(API_BASE + '/channels/');
        const data = await response.json();
        
        const container = document.getElementById('channels-container');
        
        if (data.total === 0) {
            container.innerHTML = '<div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.7);">Каналов пока нет. Создайте первый канал!</div>';
            return;
        }
        
        let channelsHTML = '';
        data.channels.forEach(channel => {
            channelsHTML += '<div class="channel-item">';
            channelsHTML += '<div class="channel-info">';
            channelsHTML += '<h4>' + channel.name + '</h4>';
            channelsHTML += '<p>' + channel.platform + ' • ' + channel.language_search + ' → ' + channel.language_publish + ' • ' + channel.style_profile + '</p>';
            channelsHTML += '</div>';
            channelsHTML += '<div style="display: flex; gap: 10px; align-items: center;">';
            const statusClass = channel.is_connected ? 'status-online' : 'status-offline';
            const statusText = channel.is_connected ? '✓ Connected' : '○ Disconnected';
            channelsHTML += '<span class="status-badge ' + statusClass + '">' + statusText + '</span>';
            channelsHTML += '<button class="btn btn-primary" onclick="editChannel(\'' + channel.id + '\')">Настроить</button>';
            channelsHTML += '</div></div>';
        });
        
        container.innerHTML = channelsHTML;
    } catch (error) {
        console.error('Ошибка загрузки каналов:', error);
    }
}

async function loadAIRouting() {
    try {
        const response = await fetch(API_BASE + '/ai/routing');
        const routing = await response.json();
        
        const container = document.getElementById('ai-routing-container');
        let routingHTML = '<div style="display: grid; gap: 15px;">';
        
        for (const [task, config] of Object.entries(routing)) {
            routingHTML += '<div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 8px;">';
            routingHTML += '<div style="display: flex; justify-content: space-between; align-items: center;">';
            routingHTML += '<div>';
            routingHTML += '<div style="font-weight: 600; margin-bottom: 5px; text-transform: capitalize;">' + task.replace('_', ' ') + '</div>';
            routingHTML += '<div style="font-size: 13px; color: rgba(255,255,255,0.7);">';
            routingHTML += 'Модель: <strong>' + config.current_model_id + '</strong> | ';
            routingHTML += 'Temp: ' + config.temperature;
            routingHTML += '</div></div>';
            routingHTML += '<button class="btn btn-primary" onclick="changeModel(\'' + task + '\')">Изменить</button>';
            routingHTML += '</div></div>';
        }
        
        routingHTML += '</div>';
        container.innerHTML = routingHTML;
    } catch (error) {
        console.error('Ошибка загрузки AI routing:', error);
    }
}

function refreshData() {
    loadAllData();
}

function showError(message) {
    const container = document.getElementById('error-container');
    container.innerHTML = '<div class="error">' + message + '</div>';
    setTimeout(() => container.innerHTML = '', 5000);
}

function showCreateChannelModal() {
    alert('Функция создания канала будет реализована в следующей версии');
}

function editChannel(channelId) {
    alert('Редактирование канала: ' + channelId);
}

function changeModel(taskName) {
    alert('Изменение модели для задачи: ' + taskName);
}
