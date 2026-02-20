// 足球数据分析大屏JavaScript
class FootballDashboard {
    constructor() {
        this.apiBase = '/api';
        this.leagueChart = null;
        this.trendChart = null;
        this.updateInterval = null;
        this.init();
    }

    async init() {
        console.log('初始化足球数据分析大屏...');
        
        // 初始化时间显示
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        
        // 加载初始数据
        await this.loadInitialData();
        
        // 启动定时更新
        this.startAutoRefresh();
        
        // 隐藏加载遮罩
        setTimeout(() => {
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        }, 1500);
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('currentTime').textContent = timeString;
    }

    async loadInitialData() {
        try {
            // 并行加载多个数据
            const [statsResponse, leaguesResponse, matchesResponse] = await Promise.all([
                fetch(`${this.apiBase}/stats`),
                fetch(`${this.apiBase}/leagues`),
                fetch(`${this.apiBase}/matches`)
            ]);

            const statsData = await statsResponse.json();
            const leaguesData = await leaguesResponse.json();
            const matchesData = await matchesResponse.json();

            if (statsData.success) {
                this.updateStats(statsData.data);
            }

            if (leaguesData.success) {
                this.updateLeagueStats(leaguesData.data);
                this.renderLeagueChart(leaguesData.data);
            }

            if (matchesData.success) {
                this.updateMatchesTable(matchesData.data);
                this.renderTrendChart(matchesData.data);
            }

            // 更新最后更新时间
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString('zh-CN');
            
        } catch (error) {
            console.error('加载数据失败:', error);
            this.showError('数据加载失败，请刷新页面重试');
        }
    }

    updateStats(stats) {
        document.getElementById('totalMatches').textContent = stats.total_matches.toLocaleString();
        document.getElementById('avgGoals').textContent = stats.avg_goals_per_match;
        document.getElementById('avgCorners').textContent = '5.2'; // 示例数据
        document.getElementById('avgYellowCards').textContent = '2.8'; // 示例数据
    }

    updateLeagueStats(leagueStats) {
        // 更新联赛统计信息到页面
        console.log('联赛统计:', leagueStats);
    }

    renderLeagueChart(leagueData) {
        const ctx = document.getElementById('leagueChart').getContext('2d');
        
        // 销毁之前的图表
        if (this.leagueChart) {
            this.leagueChart.destroy();
        }

        const labels = Object.keys(leagueData);
        const data = Object.values(leagueData).map(item => item.match_count);

        this.leagueChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: '联赛比赛分布',
                        color: '#00ff88',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }

    renderTrendChart(matchesData) {
        const ctx = document.getElementById('trendChart').getContext('2d');
        
        // 销毁之前的图表
        if (this.trendChart) {
            this.trendChart.destroy();
        }

        // 按日期分组数据
        const dateGroups = {};
        matchesData.slice(0, 30).forEach(match => {
            const date = match.date.split(' ')[0]; // 只取日期部分
            if (!dateGroups[date]) {
                dateGroups[date] = [];
            }
            dateGroups[date].push(match);
        });

        const dates = Object.keys(dateGroups).sort().slice(-10); // 最近10天
        const goalsData = dates.map(date => {
            const matches = dateGroups[date];
            return matches.reduce((sum, match) => sum + match.home_goals + match.away_goals, 0) / matches.length;
        });

        this.trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates.map(date => date.substring(5)), // 显示月日
                datasets: [{
                    label: '场均进球',
                    data: goalsData,
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#00ff88',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#fff'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#fff'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: '近期比赛趋势',
                        color: '#00ff88',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    updateMatchesTable(matches) {
        const tbody = document.querySelector('#matchesTable tbody');
        tbody.innerHTML = '';

        matches.slice(0, 10).forEach(match => {
            const row = document.createElement('tr');
            
            // 格式化日期
            const matchDate = new Date(match.date);
            const dateStr = matchDate.toLocaleDateString('zh-CN', {
                month: '2-digit',
                day: '2-digit'
            });

            row.innerHTML = `
                <td>${match.league}</td>
                <td>${dateStr}</td>
                <td>${match.home_team}</td>
                <td class="score-cell">${match.home_goals}-${match.away_goals}</td>
                <td>${match.away_team}</td>
                <td>${match.home_corners}-${match.away_corners}</td>
                <td>${match.home_yellow_cards}-${match.away_yellow_cards}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    startAutoRefresh() {
        // 每30秒刷新一次数据
        this.updateInterval = setInterval(async () => {
            try {
                const response = await fetch(`${this.apiBase}/stats`);
                const data = await response.json();
                
                if (data.success) {
                    this.updateStats(data.data);
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleString('zh-CN');
                }
            } catch (error) {
                console.error('自动刷新失败:', error);
            }
        }, 30000);
    }

    showError(message) {
        // 创建错误提示元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff4444;
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                z-index: 1000;
                max-width: 300px;
            ">
                <strong>错误:</strong> ${message}
                <button onclick="this.parentElement.remove()" style="
                    float: right;
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    margin-left: 10px;
                ">×</button>
            </div>
        `;
        document.body.appendChild(errorDiv);
        
        // 5秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }

    // 页面卸载时清理资源
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.leagueChart) {
            this.leagueChart.destroy();
        }
        if (this.trendChart) {
            this.trendChart.destroy();
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new FootballDashboard();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});