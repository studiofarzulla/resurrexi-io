/**
 * Topology Diagram Interactivity
 * Minimal JS for node hover/click interactions
 */

(function() {
    'use strict';

    // Node data
    const nodes = {
        purrpower: {
            name: 'PurrPower',
            role: 'Primary Workstation',
            cpu: 'AMD Ryzen 9 9900X (12C/24T)',
            ram: '128GB DDR5',
            gpu: '7900 XTX (24GB) + 7800 XT (16GB)',
            storage: '2TB NVMe',
            note: 'Dual GPU with cross-chassis power delivery'
        },
        sudosenpai: {
            name: 'SudoSenpai',
            role: 'Control Plane',
            cpu: 'AMD Ryzen 9 5900X (12C/24T)',
            ram: '32GB DDR4',
            storage: '5.5TB Mixed',
            note: 'K3s control plane, Cloudflare tunnel'
        },
        kawaiikali: {
            name: 'KawaiiKali',
            role: 'Mobile Lab',
            cpu: 'AMD Ryzen AI 9 HX 370 (12C/24T)',
            ram: '32GB LPDDR5X',
            npu: 'XDNA 2 (50 TOPS)',
            note: 'ASUS Zenbook S16, travel node'
        },
        croncrunch: {
            name: 'CronCrunch',
            role: 'GPU Worker',
            cpu: 'AMD Ryzen 7 2700X',
            ram: '16GB DDR4',
            gpu: 'GTX 1080 (8GB)',
            note: 'CUDA compute, older model inference'
        },
        wolfwhoami: {
            name: 'WolfWhoami',
            role: 'K3s Worker',
            cpu: 'Intel i7',
            note: 'General compute worker'
        },
        nekonetcat: {
            name: 'NekoNetcat',
            role: 'K3s Worker',
            cpu: 'Intel i5',
            note: 'Network tools, worker node'
        },
        bittybash: {
            name: 'BittyBash',
            role: 'Edge Node',
            cpu: 'Intel',
            note: 'Lightweight edge compute'
        },
        veryvuln: {
            name: 'VeryVuln',
            role: 'Honeypot',
            cpu: 'Intel Celeron',
            note: 'Intentionally vulnerable target for red team experiments',
            warning: true
        }
    };

    // Get tooltip element
    const tooltip = document.getElementById('node-tooltip');
    if (!tooltip) return;

    // Get all node groups
    const nodeElements = document.querySelectorAll('.node[data-node]');

    nodeElements.forEach(node => {
        const nodeId = node.dataset.node;
        const data = nodes[nodeId];
        if (!data) return;

        // Click handler - show detailed tooltip
        node.addEventListener('click', (e) => {
            e.stopPropagation();
            showTooltip(data, e);
        });

        // Hover effects (CSS handles most of it, but we can enhance)
        node.addEventListener('mouseenter', () => {
            node.style.filter = 'url(#glowFull)';
        });

        node.addEventListener('mouseleave', () => {
            node.style.filter = '';
        });
    });

    // Hide tooltip when clicking elsewhere
    document.addEventListener('click', () => {
        tooltip.classList.remove('visible');
    });

    function showTooltip(data, event) {
        let html = `
            <h4 style="margin: 0 0 0.5rem; color: ${data.warning ? '#ef4444' : '#a855f7'};">${data.name}</h4>
            <p style="margin: 0 0 0.75rem; font-size: 0.8rem; color: #a1a1b5;">${data.role}</p>
        `;

        if (data.cpu) html += `<div style="font-size: 0.75rem;"><strong>CPU:</strong> ${data.cpu}</div>`;
        if (data.ram) html += `<div style="font-size: 0.75rem;"><strong>RAM:</strong> ${data.ram}</div>`;
        if (data.gpu) html += `<div style="font-size: 0.75rem;"><strong>GPU:</strong> ${data.gpu}</div>`;
        if (data.npu) html += `<div style="font-size: 0.75rem;"><strong>NPU:</strong> ${data.npu}</div>`;
        if (data.storage) html += `<div style="font-size: 0.75rem;"><strong>Storage:</strong> ${data.storage}</div>`;
        if (data.note) html += `<p style="margin: 0.5rem 0 0; font-size: 0.7rem; color: #5a5a70; font-style: italic;">${data.note}</p>`;

        tooltip.innerHTML = html;
        tooltip.style.left = `${event.pageX + 15}px`;
        tooltip.style.top = `${event.pageY - 10}px`;
        tooltip.classList.add('visible');

        // Keep tooltip in viewport
        const rect = tooltip.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            tooltip.style.left = `${event.pageX - rect.width - 15}px`;
        }
        if (rect.bottom > window.innerHeight) {
            tooltip.style.top = `${event.pageY - rect.height - 10}px`;
        }
    }
})();
