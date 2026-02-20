// 比赛预测页面JavaScript
class FootballPredictor {
    constructor() {
        this.apiBase = '/api';
        this.predictionHistory = [];
        this.init();
    }

    async init() {
        console.log('初始化预测页面...');
        
        // 绑定表单提交事件
        document.getElementById('predictionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePrediction();
        });
        
        // 加载球队列表
        await this.loadTeams();
        
        // 隐藏初始加载动画（如果有）
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 1000);
        }
        
        // 加载历史记录
        this.loadHistory();
    }

    async loadTeams() {
        try {
            console.log('开始加载球队列表...');
            const response = await fetch(`${this.apiBase}/teams`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            console.log('响应状态:', response.status);
            const data = await response.json();
            console.log('球队数据:', data);
            
            if (data.success && Array.isArray(data.data)) {
                console.log('成功获取', data.data.length, '个球队');
                this.populateTeamList(data.data);
            } else {
                console.error('数据格式不正确:', data);
                this.showMessage('球队数据格式错误，请检查API返回', 'error');
            }
        } catch (error) {
            console.error('加载球队列表失败:', error);
            this.showMessage('加载球队列表失败: ' + error.message, 'error');
            // 尝试重试
            setTimeout(() => {
                this.loadTeams();
            }, 2000);
        }
    }

    populateTeamList(teams) {
        const datalist = document.getElementById('teamsList');
        datalist.innerHTML = '';
        
        teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team;
            datalist.appendChild(option);
        });
    }

    async handlePrediction() {
        const form = document.getElementById('predictionForm');
        const formData = new FormData(form);
        
        const predictionData = {
            league: formData.get('league'),
            home_team: formData.get('home_team'),
            away_team: formData.get('away_team')
        };
        
        // 验证输入
        if (!predictionData.home_team || !predictionData.away_team) {
            this.showMessage('请填写完整的球队信息', 'error');
            return;
        }
        
        if (predictionData.home_team === predictionData.away_team) {
            this.showMessage('主队和客队不能相同', 'error');
            return;
        }
        
        // 显示加载状态
        this.showLoading(true);
        
        try {
            // 先获取球队历史数据
            await this.loadTeamHistories(predictionData.home_team, predictionData.away_team);
            
            const response = await fetch(`${this.apiBase}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(predictionData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayPredictionResult(result.data);
                this.addToHistory(result.data);
                this.showMessage('预测完成!', 'success');
            } else {
                this.showMessage(result.error || '预测失败', 'error');
            }
        } catch (error) {
            console.error('预测请求失败:', error);
            this.showMessage('网络错误，请稍后重试', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayPredictionResult(data) {
        // 显示结果区域
        document.getElementById('resultsSection').style.display = 'block';
        
        // 更新比赛信息
        document.getElementById('resultHomeTeam').textContent = data.home_team;
        document.getElementById('resultAwayTeam').textContent = data.away_team;
        document.getElementById('resultLeague').textContent = data.league;
        
        // 更新预测数据
        const pred = data.prediction;
        document.getElementById('homeGoals').textContent = pred.home_team_goals;
        document.getElementById('awayGoals').textContent = pred.away_team_goals;
        document.getElementById('totalGoals').textContent = pred.total_goals;
        
        document.getElementById('homeCorners').textContent = pred.home_corners;
        document.getElementById('awayCorners').textContent = pred.away_corners;
        document.getElementById('totalCorners').textContent = pred.total_corners;
        
        document.getElementById('homeYellow').textContent = pred.home_yellow_cards;
        document.getElementById('awayYellow').textContent = pred.away_yellow_cards;
        document.getElementById('totalYellow').textContent = pred.total_yellow_cards;
        
        // 生成分析内容
        this.generateAnalysis(pred);
        
        // 滚动到结果区域
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    generateAnalysis(prediction) {
        const analysisContent = document.getElementById('analysisContent');
        const homeGoals = prediction.home_team_goals;
        const awayGoals = prediction.away_team_goals;
        const totalGoals = prediction.total_goals;
        const homeCorners = prediction.home_corners;
        const awayCorners = prediction.away_corners;
        
        let analysis = '';
        
        // 进球分析
        if (homeGoals > awayGoals) {
            analysis += `<div class="analysis-point"><strong>胜负预测:</strong> 主队${homeGoals}比${awayGoals}获胜的可能性较大</div>`;
        } else if (awayGoals > homeGoals) {
            analysis += `<div class="analysis-point"><strong>胜负预测:</strong> 客队${awayGoals}比${homeGoals}获胜的可能性较大</div>`;
        } else {
            analysis += `<div class="analysis-point"><strong>胜负预测:</strong> 比赛可能出现平局</div>`;
        }
        
        // 总进球分析
        if (totalGoals < 2.0) {
            analysis += `<div class="analysis-point"><strong>进球数:</strong> 预计是一场进球较少的比赛（${totalGoals}球）</div>`;
        } else if (totalGoals > 3.0) {
            analysis += `<div class="analysis-point"><strong>进球数:</strong> 预计是一场进球较多的比赛（${totalGoals}球）</div>`;
        } else {
            analysis += `<div class="analysis-point"><strong>进球数:</strong> 预计进球数适中（${totalGoals}球）</div>`;
        }
        
        // 角球分析
        const cornerDiff = Math.abs(homeCorners - awayCorners);
        if (cornerDiff > 3) {
            const strongerTeam = homeCorners > awayCorners ? '主队' : '客队';
            analysis += `<div class="analysis-point"><strong>角球优势:</strong> ${strongerTeam}在角球方面有明显优势</div>`;
        }
        
        // 比赛风格分析
        const avgCorners = (homeCorners + awayCorners) / 2;
        if (avgCorners > 10) {
            analysis += `<div class="analysis-point"><strong>比赛风格:</strong> 预计是一场攻势足球，创造机会较多</div>`;
        } else {
            analysis += `<div class="analysis-point"><strong>比赛风格:</strong> 预计是一场相对保守的比赛</div>`;
        }
        
        analysisContent.innerHTML = analysis;
    }

    addToHistory(predictionData) {
        const historyItem = {
            ...predictionData,
            timestamp: new Date().toISOString()
        };
        
        this.predictionHistory.unshift(historyItem);
        
        // 限制历史记录数量
        if (this.predictionHistory.length > 10) {
            this.predictionHistory.pop();
        }
        
        this.saveHistory();
        this.updateHistoryDisplay();
    }

    saveHistory() {
        localStorage.setItem('predictionHistory', JSON.stringify(this.predictionHistory));
    }

    loadHistory() {
        const saved = localStorage.getItem('predictionHistory');
        if (saved) {
            this.predictionHistory = JSON.parse(saved);
            this.updateHistoryDisplay();
        }
    }

    updateHistoryDisplay() {
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';
        
        if (this.predictionHistory.length === 0) {
            historyList.innerHTML = '<div style="text-align: center; color: #aaa; padding: 20px;">暂无预测历史</div>';
            return;
        }
        
        this.predictionHistory.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const matchInfo = `${item.home_team} vs ${item.away_team}`;
            const resultInfo = `${item.prediction.home_team_goals}-${item.prediction.away_team_goals}`;
            const timeInfo = new Date(item.timestamp).toLocaleString('zh-CN');
            
            historyItem.innerHTML = `
                <div>
                    <div class="history-match">${matchInfo}</div>
                    <div class="history-result">预测比分: ${resultInfo}</div>
                </div>
                <div class="history-time">${timeInfo}</div>
            `;
            
            historyList.appendChild(historyItem);
        });
    }

    showLoading(show) {
        const predictBtn = document.querySelector('.predict-btn');
        const btnText = predictBtn.querySelector('.btn-text');
        const btnLoading = predictBtn.querySelector('.btn-loading');
        
        if (show) {
            predictBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
        } else {
            predictBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#00aa00' : '#4444ff'};
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                z-index: 1000;
                max-width: 400px;
                text-align: center;
            ">
                ${message}
                <button onclick="this.parentElement.remove()" style="
                    float: right;
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    margin-left: 15px;
                ">×</button>
            </div>
        `;
        
        document.body.appendChild(messageDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 3000);
    }

    clearForm() {
        document.getElementById('predictionForm').reset();
        document.getElementById('resultsSection').style.display = 'none';
    }

    showNewPrediction() {
        this.clearForm();
        document.getElementById('homeTeam').focus();
    }

    sharePrediction() {
        const resultSection = document.getElementById('resultsSection');
        if (resultSection.style.display !== 'none') {
            // 这里可以实现分享功能
            this.showMessage('分享功能开发中...', 'info');
        } else {
            this.showMessage('请先进行预测', 'error');
        }
    }
    
    async loadTeamHistories(homeTeam, awayTeam) {
        try {
            // 显示历史数据区域
            document.getElementById('teamHistorySection').style.display = 'block';
            
            // 设置球队标题
            document.getElementById('homeTeamTitle').textContent = `${homeTeam} 近期战绩`;
            document.getElementById('awayTeamTitle').textContent = `${awayTeam} 近期战绩`;
            
            // 并行获取两队的历史数据
            const [homeHistory, awayHistory] = await Promise.all([
                this.fetchTeamHistory(homeTeam),
                this.fetchTeamHistory(awayTeam)
            ]);
            
            // 显示历史数据
            this.displayTeamHistory('homeTeamMatches', homeHistory.matches);
            this.displayTeamHistory('awayTeamMatches', awayHistory.matches);
            
        } catch (error) {
            console.error('加载球队历史数据失败:', error);
            // 即使历史数据加载失败，也要继续预测
        }
    }
    
    async fetchTeamHistory(teamName) {
        const response = await fetch(`/api/team_history/${encodeURIComponent(teamName)}`);
        const result = await response.json();
        return result;
    }
    
    displayTeamHistory(containerId, matches) {
        const container = document.getElementById(containerId);
        
        if (!matches || matches.length === 0) {
            container.innerHTML = '<p class="no-data">暂无该队的比赛数据</p>';
            return;
        }
        
        container.innerHTML = matches.map(match => {
            const resultClass = {
                '胜': 'result-win',
                '平': 'result-draw',
                '负': 'result-loss'
            }[match.result] || '';
            
            const teamName = containerId.includes('home') ? 
                document.getElementById('homeTeam').value : 
                document.getElementById('awayTeam').value;
            
            return `
                <div class="match-record">
                    <div class="match-line-1">
                        <span class="match-date">${match.date.substring(5, 10)}</span>
                        <span class="match-league">${match.league}</span>
                        <span class="match-teams-inline">
                            <span class="team-name">${teamName}</span>
                            <span class="role-tag">${match.role}</span>
                            <span class="vs">vs</span>
                            <span class="opponent-name">${match.opponent}</span>
                        </span>
                        <span class="match-score">${match.score}</span>
                        <span class="result-tag ${resultClass}">${match.result}</span>
                    </div>
                    <div class="match-line-2">
                        <div class="stat-item">
                            <div class="stat-label">射门</div>
                            <div class="stat-value">${match.shots}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">射正</div>
                            <div class="stat-value">${match.shots_on_target}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">控球</div>
                            <div class="stat-value">${Math.round(match.possession)}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">角球</div>
                            <div class="stat-value">${match.team_corners}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">黄牌</div>
                            <div class="stat-value">${match.team_yellow_cards}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// 全局函数供HTML调用
function clearForm() {
    if (window.predictor) {
        window.predictor.clearForm();
    }
}

function showNewPrediction() {
    if (window.predictor) {
        window.predictor.showNewPrediction();
    }
}

function sharePrediction() {
    if (window.predictor) {
        window.predictor.sharePrediction();
    }
}

function loadTeams() {
    if (window.predictor) {
        window.predictor.loadTeams();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.predictor = new FootballPredictor();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    // 清理工作
});