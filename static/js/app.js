// 主要JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    
    // 全局变量
    let isMonitoring = false;
    let statusUpdateInterval;
    
    // 初始化
    init();
    
    function init() {
        // 更新监控状态
        updateMonitoringStatus();
        
        // 启动状态轮询
        startStatusPolling();
        
        // 绑定事件
        bindEvents();
        
        // 初始化工具提示
        initTooltips();
    }
    
    // 绑定事件
    function bindEvents() {
        // 推文卡片点击事件
        const tweetCards = document.querySelectorAll('.tweet-card');
        tweetCards.forEach(card => {
            card.addEventListener('click', function() {
                const tweetId = this.dataset.tweetId;
                if (tweetId) {
                    window.location.href = `/tweet/${tweetId}`;
                }
            });
        });
        
        // 筛选表单提交事件
        const filterForm = document.getElementById('filter-form');
        if (filterForm) {
            filterForm.addEventListener('submit', function(e) {
                showLoading('正在筛选...');
            });
        }
        
        // 密码显示/隐藏切换
        initPasswordToggle();
        
        // 表单验证
        initFormValidation();
    }
    
    // 更新监控状态
    function updateMonitoringStatus() {
        fetch('/api/monitoring_status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('monitoring-status');
                if (statusElement) {
                    if (data.running) {
                        statusElement.innerHTML = '<i class="bi bi-circle-fill text-success"></i> 监控中';
                        statusElement.className = 'badge bg-success';
                        isMonitoring = true;
                    } else {
                        statusElement.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> 已停止';
                        statusElement.className = 'badge bg-danger';
                        isMonitoring = false;
                    }
                }
                
                // 更新最后更新时间
                const lastUpdateElement = document.querySelector('.navbar-text small');
                if (lastUpdateElement && data.last_update) {
                    const updateTime = new Date(data.last_update).toLocaleString('zh-CN');
                    lastUpdateElement.textContent = `最后更新: ${updateTime}`;
                }
            })
            .catch(error => {
                console.error('获取监控状态失败:', error);
            });
    }
    
    // 启动状态轮询
    function startStatusPolling() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
        
        statusUpdateInterval = setInterval(updateMonitoringStatus, 10000); // 每10秒更新一次
    }
    
    // 停止状态轮询
    function stopStatusPolling() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
    }
    
    // 显示加载状态
    function showLoading(message = '加载中...') {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div class="d-flex justify-content-center align-items-center position-fixed top-0 start-0 w-100 h-100" 
                 style="background-color: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="text-center text-white">
                    <div class="loading mb-3"></div>
                    <p>${message}</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    }
    
    // 隐藏加载状态
    function hideLoading() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    // 显示消息
    function showMessage(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 3秒后自动隐藏
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
    
    // 初始化密码显示/隐藏功能
    function initPasswordToggle() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            // 检查是否已经有切换按钮
            const existingToggle = input.parentNode.querySelector('.password-toggle');
            if (existingToggle) return;
            
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'btn btn-outline-secondary password-toggle';
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
            toggleBtn.style.cssText = 'position: absolute; right: 5px; top: 50%; transform: translateY(-50%); z-index: 10; border: none; background: transparent;';
            
            // 设置父容器样式
            input.parentNode.style.position = 'relative';
            input.style.paddingRight = '45px';
            
            toggleBtn.addEventListener('click', function() {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.innerHTML = '<i class="bi bi-eye-slash"></i>';
                } else {
                    input.type = 'password';
                    this.innerHTML = '<i class="bi bi-eye"></i>';
                }
            });
            
            input.parentNode.appendChild(toggleBtn);
        });
    }
    
    // 初始化表单验证
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    showMessage('请填写所有必需字段', 'danger');
                }
                form.classList.add('was-validated');
            });
        });
    }
    
    // 初始化工具提示
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // 复制到剪贴板功能
    window.copyToClipboard = function(text, button) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check"></i> 已复制';
                button.classList.replace('btn-outline-secondary', 'btn-success');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.replace('btn-success', 'btn-outline-secondary');
                }, 2000);
                
                showMessage('内容已复制到剪贴板', 'success');
            }).catch(function() {
                showMessage('复制失败，请手动复制', 'danger');
            });
        } else {
            // 备用方案：使用execCommand
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                showMessage('内容已复制到剪贴板', 'success');
            } catch (err) {
                showMessage('复制失败，请手动复制', 'danger');
            }
            document.body.removeChild(textArea);
        }
    };
    
    // 格式化时间
    window.formatTime = function(timeString) {
        const date = new Date(timeString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };
    
    // 截断文本
    window.truncateText = function(text, maxLength = 100) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    };
    
    // 防抖函数
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // 页面离开时清理
    window.addEventListener('beforeunload', function() {
        stopStatusPolling();
    });
    
    // 暴露全局函数
    window.TwitterAI = {
        updateMonitoringStatus: updateMonitoringStatus,
        showLoading: showLoading,
        hideLoading: hideLoading,
        showMessage: showMessage,
        startStatusPolling: startStatusPolling,
        stopStatusPolling: stopStatusPolling
    };
});

// API调用封装
class API {
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || '请求失败');
            }
            
            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
    
    static async saveConfig(config) {
        return this.request('/api/save_config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }
    
    static async startMonitoring() {
        return this.request('/api/start_monitoring', {
            method: 'POST'
        });
    }
    
    static async stopMonitoring() {
        return this.request('/api/stop_monitoring', {
            method: 'POST'
        });
    }
    
    static async getMonitoringStatus() {
        return this.request('/api/monitoring_status');
    }
    
    static async getTweets(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/api/tweets?${params}`);
    }
}

// 暴露API类
window.API = API; 