// 新增的提示框功能
const tooltip = document.getElementById('column-tooltip');
        
// 獲取表頭的tooltiptext內容
function getHeaderContent(columnIndex) {
    const header = document.querySelector(`thead th:nth-child(${columnIndex + 1})`);
    const tooltipDiv = header.querySelector('.tooltip');
    if (tooltipDiv) {
        const title = tooltipDiv.dataset.title;
        const content = tooltipDiv.dataset.content;
        if (title && content) {
            return { title, content };
        }
    }
    return null;
}

// 為表格添加滑鼠事件監聽器
document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('table');
    const tooltip = document.getElementById('column-tooltip');

    // 當滑鼠移到表格單元格上時
    table.addEventListener('mouseover', (e) => {
        const cell = e.target.closest('td, th');
        if (cell) {
            const cellIndex = cell.cellIndex;
            const headerContent = getHeaderContent(cellIndex);
            
            if (headerContent) {
                tooltip.innerHTML = `
                    <h3 style="color: #007BFF; margin: 0 0 8px 0; font-size: 16px;">${headerContent.title}</h3>
                    <p style="margin: 0; line-height: 1.4; color: white; font-size: 14px;">${headerContent.content}</p>
                `;
                tooltip.style.display = 'block';
            } else {
                tooltip.style.display = 'none';
            }
        }
    });

    // 當滑鼠離開表格單元格時
    table.addEventListener('mouseout', (e) => {
        const relatedTarget = e.relatedTarget;
        if (!relatedTarget || !relatedTarget.closest('td, th')) {
            tooltip.style.display = 'none';
        }
    });
});

// 更新提示框位置並處理邊界情況
document.addEventListener('mousemove', (e) => {
    if (tooltip.style.display === 'block') {
        const padding = 15;
        const tooltipRect = tooltip.getBoundingClientRect();

        // 獲取滾動距離
        const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
        const scrollY = window.pageYOffset || document.documentElement.scrollTop;
        
        // 計算新位置
        let left = e.clientX + padding;
        let top = e.clientY + padding;

        // 檢查是否會超出視窗右邊界
        if (left + tooltipRect.width > window.innerWidth) {
            left = e.clientX - tooltipRect.width - padding;
        }

        // 檢查是否會超出視窗下邊界
        if (top + tooltipRect.height > window.innerHeight) {
            top = e.clientY - tooltipRect.height - padding;
        }

        // 確保提示框不會出現在負值位置
        left = Math.max(padding, left);
        top = Math.max(padding, top);

        tooltip.style.left = `${left + scrollX}px`;
        tooltip.style.top = `${top + scrollY}px`;
    }
});