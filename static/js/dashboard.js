(function () {
    const elementoDados = document.getElementById("dados-dashboard");
    const canvasCurvaS = document.getElementById("grafico-curva-s");
    if (!elementoDados || !canvasCurvaS) {
        return;
    }
    const dados = JSON.parse(elementoDados.textContent);
    if (!dados.curvaS || dados.curvaS.length === 0) {
        return;
    }

    const estilo = getComputedStyle(document.documentElement);
    const cor = (variavel) => estilo.getPropertyValue(variavel).trim();

    const corSerie = cor("--serie-1");
    const corSerieFraca = cor("--serie-1-fraca");
    const corGrade = cor("--linha-grade");
    const corTextoMudo = cor("--texto-mudo");
    const corTextoPrimario = cor("--texto-primario");
    const corSuperficie = cor("--superficie");

    function formatarMoeda(valor) {
        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL",
            maximumFractionDigits: 0,
        }).format(valor);
    }

    new Chart(canvasCurvaS, {
        type: "line",
        data: {
            labels: dados.curvaS.map((ponto) => ponto.competencia),
            datasets: [
                {
                    label: "Acumulado planejado",
                    data: dados.curvaS.map((ponto) => ponto.acumulado),
                    borderColor: corSerie,
                    backgroundColor: corSerieFraca,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: corSerie,
                    pointHoverBorderColor: corSuperficie,
                    pointHoverBorderWidth: 2,
                    fill: true,
                    tension: 0.35,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: corSuperficie,
                    titleColor: corTextoPrimario,
                    bodyColor: corTextoPrimario,
                    borderColor: corGrade,
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: (contexto) => formatarMoeda(contexto.raw),
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    border: { color: corGrade },
                    ticks: { color: corTextoMudo, font: { size: 11 } },
                },
                y: {
                    grid: { color: corGrade, drawTicks: false },
                    border: { display: false },
                    ticks: {
                        color: corTextoMudo,
                        font: { size: 11 },
                        callback: (valor) => formatarMoeda(valor),
                    },
                },
            },
        },
    });
})();
