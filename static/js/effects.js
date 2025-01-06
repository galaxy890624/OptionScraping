// 游標光暈效果
const cursorGlow = document.getElementById('cursor-glow');
        
// 創建 SVG 元素
const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
svg.setAttribute("width", "100");
svg.setAttribute("height", "100");

// 創建三個圓形，形成多層光暈效果
const circles = [
    {radius: 40, color: "rgba(0, 128, 255, 0.1)"},
    {radius: 20, color: "rgba(0, 128, 255, 0.2)"},
    {radius: 5, color: "rgba(255, 255, 255, 0.5)"}
];

circles.forEach(({radius, color}) => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", "50");
    circle.setAttribute("cy", "50");
    circle.setAttribute("r", radius.toString());
    circle.setAttribute("fill", color);
    circle.setAttribute("filter", "blur(3px)");
    svg.appendChild(circle);
});

cursorGlow.appendChild(svg);

// 星星軌跡效果
const starsContainer = document.getElementById('stars-container');
let lastStarTime = 0;
const starInterval = 20; // 每 20ms 產生一顆星星

document.addEventListener('mousemove', (e) => {
    // 更新光暈位置
    cursorGlow.style.left = (e.clientX - 50) + 'px';
    cursorGlow.style.top = (e.clientY - 50) + 'px';

    // 創建星星
    const currentTime = Date.now();
    if (currentTime - lastStarTime > starInterval) {
        createStar(e.clientX, e.clientY);
        lastStarTime = currentTime;
    }

    // 表格 如果tooltip是可見的,就更新它的位置
    if (tooltip.style.display === 'block') {
        tooltip.style.left = e.pageX + 10 + 'px';
        tooltip.style.top = e.pageY + 10 + 'px';
    }
});

function createStar(x, y) {
    const star = document.createElement('div');
    star.className = 'star';
    
    // 隨機大小
    const size = Math.random() * 3 + 2;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    
    // 隨機起始位置（在游標周圍小範圍內）
    const offsetX = (Math.random() - 0.5) * 10;
    const offsetY = (Math.random() - 0.5) * 10;
    star.style.left = (x + offsetX) + 'px';
    star.style.top = (y + offsetY) + 'px';
    
    // 隨機顏色（藍白色系）
    const hue = Math.random() * 40 + 200; // 200-240 之間的色相值
    const saturation = Math.random() * 50 + 50; // 50-100% 的飽和度
    const lightness = Math.random() * 30 + 70; // 70-100% 的亮度
    star.style.background = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    
    // 添加模糊效果
    star.style.filter = 'blur(0.5px)';
    
    // 添加到容器
    starsContainer.appendChild(star);
    
    // 動畫結束後移除元素
    setTimeout(() => {
        star.remove();
    }, 1000);
}