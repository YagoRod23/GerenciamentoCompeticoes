/**
 * Arquivo JavaScript principal da aplicação web
 */

// Aguarda o carregamento do DOM
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initSidebar();
    initAlerts();
    initForms();
    initTables();
    initModals();
    initTooltips();
    
    console.log('Sistema de Gerenciamento Esportivo carregado!');
});

/**
 * Inicializa funcionalidades da sidebar
 */
function initSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Marcar item ativo no menu
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Inicializa alertas com auto-dismiss
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-dismiss após 5 segundos
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }, 5000);
        
        // Botão de fechar
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.transition = 'opacity 0.3s';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            });
        }
    });
}

/**
 * Inicializa funcionalidades de formulários
 */
function initForms() {
    // Validação em tempo real
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateInput(this);
                }
            });
        });
        
        // Validação no submit
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Por favor, corrija os erros no formulário.', 'danger');
            }
        });
    });
}

/**
 * Valida um input específico
 */
function validateInput(input) {
    const value = input.value.trim();
    let isValid = true;
    let message = '';
    
    // Remover classes de validação existentes
    input.classList.remove('is-valid', 'is-invalid');
    
    // Verificar se é obrigatório
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        message = 'Este campo é obrigatório.';
    }
    
    // Validações específicas por tipo
    if (value && input.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Por favor, insira um email válido.';
        }
    }
    
    if (value && input.type === 'tel') {
        const phoneRegex = /^(\(?\d{2}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            message = 'Por favor, insira um telefone válido.';
        }
    }
    
    if (value && input.getAttribute('minlength')) {
        const minLength = parseInt(input.getAttribute('minlength'));
        if (value.length < minLength) {
            isValid = false;
            message = `Este campo deve ter pelo menos ${minLength} caracteres.`;
        }
    }
    
    // Aplicar classes de validação
    if (isValid) {
        input.classList.add('is-valid');
    } else {
        input.classList.add('is-invalid');
        showInputError(input, message);
    }
    
    return isValid;
}

/**
 * Mostra erro em um input
 */
function showInputError(input, message) {
    // Remover mensagem de erro existente
    const existingError = input.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Criar nova mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    input.parentNode.appendChild(errorDiv);
}

/**
 * Inicializa funcionalidades de tabelas
 */
function initTables() {
    // Ordenação de tabelas
    const sortableTables = document.querySelectorAll('.table-sortable');
    
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, header.dataset.sort);
            });
        });
    });
    
    // Filtro de tabelas
    const searchInputs = document.querySelectorAll('[data-table-search]');
    
    searchInputs.forEach(input => {
        const tableId = input.dataset.tableSearch;
        const table = document.getElementById(tableId);
        
        if (table) {
            input.addEventListener('input', () => {
                filterTable(table, input.value);
            });
        }
    });
}

/**
 * Ordena tabela por coluna
 */
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-value="${column}"]`)?.textContent || 
                      a.cells[parseInt(column)]?.textContent || '';
        const bValue = b.querySelector(`[data-value="${column}"]`)?.textContent || 
                      b.cells[parseInt(column)]?.textContent || '';
        
        return aValue.localeCompare(bValue, 'pt-BR', { numeric: true });
    });
    
    // Limpar tbody e adicionar linhas ordenadas
    tbody.innerHTML = '';
    sortedRows.forEach(row => tbody.appendChild(row));
}

/**
 * Filtra tabela por texto
 */
function filterTable(table, searchText) {
    const rows = table.querySelectorAll('tbody tr');
    const search = searchText.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

/**
 * Inicializa modais
 */
function initModals() {
    // Botões que abrem modais
    const modalTriggers = document.querySelectorAll('[data-modal]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modal;
            const modal = document.getElementById(modalId);
            
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    // Fechar modais
    const modalCloses = document.querySelectorAll('.modal-close');
    
    modalCloses.forEach(close => {
        close.addEventListener('click', () => {
            const modal = close.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        });
    });
    
    // Fechar modal clicando no overlay
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            hideModal(e.target.querySelector('.modal'));
        }
    });
}

/**
 * Mostra modal
 */
function showModal(modal) {
    modal.style.display = 'block';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

/**
 * Esconde modal
 */
function hideModal(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

/**
 * Inicializa tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Mostra tooltip
 */
function showTooltip(e) {
    const element = e.target;
    const text = element.dataset.tooltip;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#333';
    tooltip.style.color = 'white';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.zIndex = '9999';
    tooltip.style.pointerEvents = 'none';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    element._tooltip = tooltip;
}

/**
 * Esconde tooltip
 */
function hideTooltip(e) {
    const element = e.target;
    if (element._tooltip) {
        document.body.removeChild(element._tooltip);
        delete element._tooltip;
    }
}

/**
 * Mostra alerta
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || 
                          document.querySelector('.main-content') || 
                          document.body;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} fade-in`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="alert-close" style="float: right; background: none; border: none; font-size: 18px; cursor: pointer;">&times;</button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-dismiss
    setTimeout(() => {
        if (alert.parentNode) {
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }
    }, 5000);
    
    // Botão fechar
    alert.querySelector('.alert-close').addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    });
}

/**
 * Confirma ação
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Formata data para exibição
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

/**
 * Formata datetime para exibição
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

/**
 * Valida CPF
 */
function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');
    
    if (cpf.length !== 11 || !!cpf.match(/(\d)\1{10}/)) {
        return false;
    }
    
    let sum = 0;
    let remainder;
    
    for (let i = 1; i <= 9; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }
    
    remainder = (sum * 10) % 11;
    
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(9, 10))) return false;
    
    sum = 0;
    for (let i = 1; i <= 10; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }
    
    remainder = (sum * 10) % 11;
    
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(10, 11))) return false;
    
    return true;
}

/**
 * Máscara para telefone
 */
function phoneMask(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{4})(\d)/, '$1-$2')
        .replace(/(\d{4})-(\d)(\d{4})/, '$1$2-$3')
        .replace(/(-\d{4})\d+?$/, '$1');
}

/**
 * Máscara para CPF
 */
function cpfMask(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})/, '$1-$2')
        .replace(/(-\d{2})\d+?$/, '$1');
}

// Aplicar máscaras automaticamente
document.addEventListener('DOMContentLoaded', function() {
    // Máscara de telefone
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = phoneMask(e.target.value);
        });
    });
    
    // Máscara de CPF
    const cpfInputs = document.querySelectorAll('input[data-mask="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = cpfMask(e.target.value);
        });
    });
});
