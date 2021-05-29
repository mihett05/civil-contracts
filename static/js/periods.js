class Period extends HTMLElement {
    connectedCallback() {
        let services = []
        if (this.getAttribute('services')) {
            services = this.getAttribute('services').split(',').map((v) => {
                return parseInt(v, 10);
            });
        }

        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
        this.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <form action="/periods/edit/${this.getAttribute('id')}/" method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
                        <div class="mb-3 row">
                            <label class="col-sm-2 col-form-label" for="period-start-${this.getAttribute('id')}">
                                Дата начала
                            </label>
                            <div class="col-sm-10">
                                <input
                                    type="text"
                                    class="form-control"
                                    value="${this.getAttribute('start')}"
                                    id="period-start-${this.getAttribute('id')}"
                                    name="start"
                                >
                            </div>
                        </div>
                        <div class="mb-3 row">
                            <label class="col-sm-2 col-form-label" for="period-end-${this.getAttribute('id')}">
                                Дата окончания
                            </label>
                            <div class="col-sm-10">
                                <input
                                    type="text"
                                    class="form-control"
                                    value="${this.getAttribute('end')}"
                                    id="period-end-${this.getAttribute('id')}"
                                    name="end"
                                >
                            </div>
                        </div>
                        <div class="mb-3 row">
                            <label class="col-sm-2 col-form-label" for="period-price-${this.getAttribute('id')}">
                                Стоимость
                            </label>
                            <div class="col-sm-10">
                                <input
                                    type="text"
                                    class="form-control"
                                    value="${this.getAttribute('price')}"
                                    id="period-price-${this.getAttribute('id')}"
                                    name="price"
                                >
                            </div>
                        </div>
                        <div class="mb-3 row">
                            <label class="form-label">Услуги</label>
                            ${Object.keys(Period.services).map((v) => `
                                <div class="form-check">
                                    <input
                                        class="form-check-input"
                                        type="checkbox"
                                        value="${v}"
                                        id="service_checkbox_${v}"
                                        ${services.includes(parseInt(v))? 'checked' : ''}
                                        name="services"
                                    >
                                    <label class="form-check-label" for="service_checkbox_${v}">
                                        ${Period.services[v]}
                                    </label>
                                </div>
                            `).join('\n')}
                        </div>
                        <div class="d-flex flex-row-reverse">
                            <button type="button" class="btn btn-danger ms-1" onclick="deletePeriod(${this.getAttribute('id')})">
                                Удалить
                            </button>
                            <button type="submit" class="btn btn-primary">
                                Изменить
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        Period.pickers[this.getAttribute('id')] = new Litepicker({
            element: document.querySelector(`#period-start-${this.getAttribute('id')}`),
            elementEnd: document.querySelector(`#period-end-${this.getAttribute('id')}`),
            singleMode: false,
            allowRepick: true,
        });
    }

    disconnectedCallback() {
        delete Period.pickers[this.getAttribute('id')];
    }

    static pickers = {};
    static services = {};

    static get observedAttributes() {
        return ['id', 'start', 'end', 'price', 'services'];
    }
}

customElements.define('period-card', Period);

const getPeriods = (workerId) => {
    const tag = document.querySelector('#periods');
    tag.innerHTML = `
        <center>
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
        </center>
    `;
    return fetch('/periods/services/list/')
        .then((response) => response.json())
        .then((data) => {
            Period.services = data;
        })
        .then(() => {
            return fetch(`/periods/${workerId}/`)
                .then((v) => {
                    tag.innerHTML = '';
                    return v.json();
                })
                .then((periods) => {
                    for (let i = 0; i < Math.ceil(periods.periods.length / 2); i++) {
                        const row = document.createElement('div');
                        row.setAttribute('class', 'row');

                        for (let j = 0; j < 2; j++) {
                            const period = periods.periods[i * 2 + j];
                            if (period) {
                                const col = document.createElement('div');
                                col.setAttribute('class', 'col-sm-6');

                                const el = document.createElement('period-card');
                                Period.observedAttributes.forEach(
                                    (key) => el.setAttribute(key, period[key])
                                );
                                el.setAttribute('services', period.services.join(','));
                                col.append(el);
                                row.append(col);
                            }
                        }
                        tag.append(document.createElement('br'));
                        tag.append(row);
                    }
                });
        });
};

const deletePeriod = (periodId) => {
    if (confirm('Удалить период?')) {
        location.href = `/periods/delete/${periodId}/${location.search}`;
    }
};

window.onload = () => {
    const select = document.querySelector('#worker_field');
    getPeriods(select.value).then(() => {
        select.addEventListener('change', (event) => {
            const button = document.querySelector('#period_add_button');
            button.setAttribute('href', `/periods/add/${event.target.value}`);
            history.pushState(null, null, `/periods/?selected=${event.target.value}`)
            return getPeriods(event.target.value);
        });
    });
};

