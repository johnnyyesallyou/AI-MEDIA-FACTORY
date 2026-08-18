const API_BASE = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    bindNavigation();
    bindChannelForm();
    loadAllData();
});

function bindNavigation() {
    document.querySelectorAll('.nav-item').forEach((button) => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const target = document.getElementById(targetId);
            if (!target) {
                return;
            }

            document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
            button.classList.add('active');
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

async function loadAllData() {
    try {
        await Promise.all([
            loadDashboardStats(),
            loadSystemHealth(),
            loadChannels(),
            loadContentPipeline(),
            loadAIRouting(),
            loadActivityFeed(),
            loadRecommendationPanel(),
            loadAutomation()
        ]);
    } catch (error) {
        showError('Ошибка загрузки данных: ' + error.message);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch(API_BASE + '/dashboard/stats');
        const stats = await response.json();

        const totalPosts = Number(stats.posts_created || 0);
        const connectedChannels = await getConnectedChannelsCount();
        const activeAgents = 7;

        const container = document.getElementById('stats-container');
        container.innerHTML = [
            '<div class="stat-card"><h3>📺 Telegram Channels</h3><div class="value">' + connectedChannels + '</div><div class="trend">active network</div></div>',
            '<div class="stat-card"><h3>🤖 Active Agents</h3><div class="value">' + activeAgents + '</div><div class="trend">research + writing + publisher</div></div>',
            '<div class="stat-card"><h3>📰 Posts Today</h3><div class="value">' + totalPosts + '</div><div class="trend">created in pipeline</div></div>',
            '<div class="stat-card"><h3>✅ Published</h3><div class="value">' + (stats.posts_published || 0) + '</div><div class="trend">manual or approved flow</div></div>',
            '<div class="stat-card"><h3>⏳ Pending Review</h3><div class="value">' + (stats.drafts_pending || 0) + '</div><div class="trend">waiting for approval</div></div>',
            '<div class="stat-card"><h3>📈 Revenue Forecast</h3><div class="value">135k ₽</div><div class="trend">forecast from active channels</div></div>'
        ].join('');
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

async function getConnectedChannelsCount() {
    try {
        const response = await fetch(API_BASE + '/channels/');
        const data = await response.json();
        return data.channels.filter((channel) => channel.is_connected).length;
    } catch (error) {
        return 0;
    }
}

async function loadSystemHealth() {
    try {
        const response = await fetch(API_BASE + '/dashboard/health');
        const health = await response.json();

        const container = document.getElementById('health-container');
        let healthHTML = '<div class="mini-grid">';

        for (const [name, service] of Object.entries(health.services)) {
            const statusClass = service.status === 'OK' ? 'status-online' : 'status-offline';
            healthHTML += '<div class="mini-card">';
            healthHTML += '<div style="font-weight: 700; margin-bottom: 6px;">' + name + '</div>';
            healthHTML += '<span class="status-badge ' + statusClass + '">' + service.status + '</span>';
            if (service.latency_ms) {
                healthHTML += '<div style="font-size: 12px; margin-top: 8px; color: #9fb8d8;">' + service.latency_ms + ' ms</div>';
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
            container.innerHTML = '<div style="text-align: center; padding: 40px; color: #9fb8d8;">Каналов пока нет. Создайте первый канал!</div>';
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
            channelsHTML += '<button class="btn btn-muted" onclick="editChannel(\'' + channel.id + '\')">Настроить</button>';
            channelsHTML += '</div></div>';
        });

        container.innerHTML = channelsHTML;
    } catch (error) {
        console.error('Ошибка загрузки каналов:', error);
    }
}

async function loadContentPipeline() {
    try {
        const response = await fetch(API_BASE + '/content/?limit=100');
        const data = await response.json();
        const container = document.getElementById('content-pipeline');

        const statusOrder = ['research', 'draft', 'review', 'approved', 'scheduled', 'published', 'rejected'];
        const grouped = statusOrder.reduce((acc, status) => ({ ...acc, [status]: [] }), {});

        data.items.forEach(item => {
            if (grouped[item.status] !== undefined) {
                grouped[item.status].push(item);
            }
        });

        const summary = statusOrder.map((status) => {
            const count = grouped[status].length;
            return '<div class="pipeline-item"><strong>' + status.toUpperCase() + '</strong><small>items: ' + count + '</small></div>';
        }).join('');

        const columns = statusOrder.map((status) => {
            const items = grouped[status];
            const cards = items.map((item) => {
                let actionButton = '';
                if (item.status === 'draft' || item.status === 'review') {
                    actionButton = '<button class="btn btn-primary" onclick="approveContent(\'' + item.id + '\')">Approve</button>';
                } else if (item.status === 'approved') {
                    actionButton = '<button class="btn btn-primary" onclick="publishContent(\'' + item.id + '\')">Publish</button>';
                }

                return '<div class="pipeline-item">'
                    + '<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">'
                    + '<div>'
                    + '<div style="font-weight: 700; margin-bottom: 5px;">' + (item.headline || 'Untitled item') + '</div>'
                    + '<small>Status: ' + item.status + '</small>'
                    + '</div>'
                    + '<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">'
                    + actionButton
                    + '</div>'
                    + '</div>'
                    + '</div>';
            }).join('');

            return '<div style="margin-top: 14px; padding: 14px; border-radius: 10px; background: rgba(255,255,255,0.04);">'
                + '<div style="font-weight: 700; margin-bottom: 10px; text-transform: uppercase;">' + status + ' (' + items.length + ')</div>'
                + '<div style="display: grid; gap: 10px;">'
                + (cards || '<div class="loading">No items</div>')
                + '</div>'
                + '</div>';
        }).join('');

        container.innerHTML = summary + columns;
    } catch (error) {
        console.error('Ошибка загрузки pipeline:', error);
    }
}

async function approveContent(contentId) {
    try {
        const response = await fetch(API_BASE + '/content/' + contentId + '/approve', {
            method: 'POST'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Не удалось approve контент');
        }
        showError('Контент approved: ' + data.headline);
        await loadAllData();
    } catch (error) {
        console.error('Ошибка approve:', error);
        showError(error.message || 'Ошибка approve');
    }
}

async function publishContent(contentId) {
    try {
        const response = await fetch(API_BASE + '/content/' + contentId + '/publish', {
            method: 'POST'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Не удалось опубликовать контент');
        }
        showError('Контент опубликован в Telegram: ' + (data.chat_id || ''));
        await loadAllData();
    } catch (error) {
        console.error('Ошибка publish:', error);
        showError(error.message || 'Ошибка publish');
    }
}

async function loadActivityFeed() {
    const feed = document.getElementById('activity-feed');
    const items = [
        { time: '14:05', title: 'AI News Collector', text: 'Собрано 42 потенциальных темы из RSS, Telegram и СМИ' },
        { time: '14:06', title: 'Content Filter', text: 'Удалено 7 дублей и отсеяно нерелевантные материалы' },
        { time: '14:07', title: 'AI Writer', text: 'Сформирован пост под стиль канала Tech Future' },
        { time: '14:08', title: 'Image Agent', text: 'Сгенерирован визуальный asset для поста' },
        { time: '14:09', title: 'Publisher', text: 'Подтверждён и отправлен в Telegram' }
    ];

    feed.innerHTML = items.map(item => {
        return '<div class="feed-item"><small>' + item.time + '</small><div style="font-weight: 700; margin: 4px 0;">' + item.title + '</div><div>' + item.text + '</div></div>';
    }).join('');
}

async function loadRecommendationPanel() {
    try {
        const response = await fetch(API_BASE + '/dashboard/workflow');
        const workflow = await response.json();
        const panel = document.getElementById('recommendation-panel');

        const workflowNodes = Array.isArray(workflow?.nodes) ? workflow.nodes : [];
        const steps = workflowNodes.map((node) => {
            return '<div class="mini-card"><strong>' + node.type + '</strong><div style="font-size: 12px; color: #9fb8d8;">workflow node</div></div>';
        }).join('');

        const workflowListResponse = await fetch(API_BASE + '/workflows/');
        const workflowList = await workflowListResponse.json();
        const templateItems = Array.isArray(workflowList?.items) ? workflowList.items : [];
        const templateOptions = templateItems.map((item) => {
            return '<div class="mini-card"><strong>' + item.name + '</strong><div style="font-size: 12px; color: #9fb8d8;">' + item.description + '</div></div>';
        }).join('');

        panel.innerHTML = [
            '<div style="display: grid; gap: 12px;">',
            '<div class="mini-card"><strong>Workflow Engine</strong><div style="font-size: 12px; color: #9fb8d8;">Data-defined pipeline for future channels and platforms</div></div>',
            steps || '<div class="mini-card"><strong>Default workflow</strong><div style="font-size: 12px; color: #9fb8d8;">No workflow nodes were returned by the API.</div></div>',
            '<div class="mini-card"><strong>' + (workflow?.name || 'Workflow Engine') + '</strong><div style="font-size: 12px; color: #9fb8d8;">' + (workflow?.description || 'Pipeline definition is available for the dashboard.') + '</div></div>',
            templateOptions || '<div class="mini-card"><strong>Templates</strong><div style="font-size: 12px; color: #9fb8d8;">No workflow templates were returned yet.</div></div>',
            '</div>'
        ].join('');
    } catch (error) {
        console.error('Ошибка загрузки workflow:', error);
        const panel = document.getElementById('recommendation-panel');
        panel.innerHTML = '<div class="mini-card"><strong>Workflow Engine</strong><div style="font-size: 12px; color: #9fb8d8;">Fallback: data-driven pipeline is ready for extension</div></div>';
    }
}

async function loadAIRouting() {
    try {
        const response = await fetch(API_BASE + '/ai/routing');
        const routing = await response.json();

        const container = document.getElementById('ai-routing-container');
        let routingHTML = '<div style="display: grid; gap: 15px;">';

        for (const [task, config] of Object.entries(routing)) {
            routingHTML += '<div style="background: rgba(255,255,255,0.05); padding: 18px; border-radius: 10px;">';
            routingHTML += '<div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">';
            routingHTML += '<div>';
            routingHTML += '<div style="font-weight: 700; margin-bottom: 4px; text-transform: capitalize;">' + task.replace('_', ' ') + '</div>';
            routingHTML += '<div style="font-size: 13px; color: #9fb8d8;">Модель: <strong>' + config.current_model_id + '</strong> | Temp: ' + config.temperature + '</div>';
            routingHTML += '</div>';
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

function bindChannelForm() {
    document.getElementById('channel-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        await saveChannelForm();
    });
}

async function loadWorkflowOptions() {
    try {
        const response = await fetch(API_BASE + '/workflows/');
        const data = await response.json();
        const select = document.getElementById('channel-workflow');
        const options = Array.isArray(data?.items) ? data.items : [];
        select.innerHTML = '<option value="">Выберите workflow</option>' + options.map((item) => {
            return '<option value="' + item.id + '">' + item.name + '</option>';
        }).join('');
    } catch (error) {
        console.error('Ошибка загрузки workflow options:', error);
    }
}

function openChannelModal(channel = null) {
    const modal = document.getElementById('channel-modal');
    const form = document.getElementById('channel-form');
    const title = document.getElementById('channel-modal-title');
    const channelId = document.getElementById('channel-id');

    form.reset();
    loadWorkflowOptions();

    if (channel) {
        document.getElementById('channel-name').value = channel.name || '';
        document.getElementById('channel-platform').value = channel.platform || 'telegram';
        document.getElementById('channel-language-search').value = channel.language_search || 'en';
        document.getElementById('channel-language-publish').value = channel.language_publish || 'ru';
        document.getElementById('channel-style-profile').value = channel.style_profile || 'minimal';
        document.getElementById('channel-timezone').value = channel.timezone || 'UTC';
        document.getElementById('channel-description').value = channel.description || '';
        channelId.value = channel.id || '';
        title.textContent = 'Редактировать канал';
    } else {
        channelId.value = '';
        title.textContent = 'Новый канал';
        document.getElementById('channel-platform').value = 'telegram';
        document.getElementById('channel-language-search').value = 'en';
        document.getElementById('channel-language-publish').value = 'ru';
        document.getElementById('channel-style-profile').value = 'minimal';
        document.getElementById('channel-timezone').value = 'UTC';
    }

    modal.classList.add('show');
}

function closeChannelModal() {
    document.getElementById('channel-modal').classList.remove('show');
}

async function saveChannelForm() {
    const form = document.getElementById('channel-form');
    const channelId = document.getElementById('channel-id').value;
    const payload = {
        name: document.getElementById('channel-name').value,
        platform: document.getElementById('channel-platform').value,
        language_search: document.getElementById('channel-language-search').value,
        language_publish: document.getElementById('channel-language-publish').value,
        style_profile: document.getElementById('channel-style-profile').value,
        timezone: document.getElementById('channel-timezone').value,
        workflow_id: document.getElementById('channel-workflow').value || null,
        description: document.getElementById('channel-description').value || null,
    };

    try {
        const method = channelId ? 'PUT' : 'POST';
        const url = channelId ? API_BASE + '/channels/' + channelId : API_BASE + '/channels/';
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Не удалось сохранить канал');
        }
        closeChannelModal();
        showError('Канал сохранён: ' + data.name);
        await loadAllData();
    } catch (error) {
        console.error('Ошибка сохранения канала:', error);
        showError(error.message || 'Ошибка сохранения канала');
    }
}

function showError(message) {
    const container = document.getElementById('error-container');
    container.innerHTML = '<div class="error">' + message + '</div>';
    setTimeout(() => container.innerHTML = '', 5000);
}

function showCreateChannelModal() {
    openChannelModal();
}

async function editChannel(channelId) {
    try {
        const response = await fetch(API_BASE + '/channels/' + channelId);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Не удалось загрузить канал');
        }
        openChannelModal(data);
    } catch (error) {
        console.error('Ошибка редактирования канала:', error);
        showError(error.message || 'Ошибка редактирования канала');
    }
}

function changeModel(taskName) {
    alert('Изменение модели для задачи: ' + taskName);
}



async function loadAutomation() {
    try {
        const response = await fetch(API_BASE + '/automation/');
        const config = await response.json();

        const container = document.getElementById('automation-container');

        if (!container) {
            return;
        }

        const engines = config.engines || {};

        container.innerHTML = `
            <div class="mini-grid">

                <div class="mini-card">
                    <strong>Global Automation</strong>
                    <div class="status-badge ${config.is_global_automation_on ? 'status-online' : 'status-offline'}">
                        ${config.is_global_automation_on ? 'ON' : 'OFF'}
                    </div>
                </div>

                <div class="mini-card">
                    <strong>Research Interval</strong>
                    <div>${config.research_interval_minutes} min</div>
                </div>

                <div class="mini-card">
                    <strong>Max Posts / Day</strong>
                    <div>${config.max_posts_per_day}</div>
                </div>

                <div class="mini-card">
                    <strong>Publish Times</strong>
                    <div>${(config.publish_times || []).join(', ')}</div>
                </div>

            </div>

            <h3 style="margin-top:20px;">Pipeline Engines</h3>

            <div class="mini-grid">

                ${Object.entries(engines).map(([name, enabled]) => `
                    <div class="mini-card">
                        <strong>${name}</strong>
                        <div class="status-badge ${enabled ? 'status-online' : 'status-offline'}">
                            ${enabled ? 'ACTIVE' : 'DISABLED'}
                        </div>
                    </div>
                `).join('')}

            </div>

            <div style="margin-top:20px;">
                <button class="btn btn-primary" onclick="runAutomationNow()">
                    ▶ Run Now
                </button>

                <button class="btn btn-muted" onclick="toggleAutomation()">
                    Toggle Automation
                </button>
            </div>
        `;

    } catch (error) {
        console.error('Ошибка загрузки automation:', error);
    }
}


async function runAutomationNow() {
    try {
        const response = await fetch(API_BASE + '/automation/run-now', {
            method: 'POST'
        });

        const data = await response.json();

        showError(
            'Automation запуск: ' + (data.status || 'started')
        );

        await loadAutomation();

    } catch(error) {
        showError(error.message);
    }
}


async function toggleAutomation() {

    try {

        const response = await fetch(API_BASE + '/automation/');
        const config = await response.json();

        config.is_global_automation_on =
            !config.is_global_automation_on;


        await fetch(API_BASE + '/automation/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });


        await loadAutomation();

    } catch(error) {
        showError(error.message);
    }
}

