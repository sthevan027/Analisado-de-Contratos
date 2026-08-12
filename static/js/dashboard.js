(function () {
    const elementoDados = document.getElementById("dados-dashboard");
    if (!elementoDados) {
        return;
    }
    const dados = JSON.parse(elementoDados.textContent);

    function formatarMoeda(valor) {
        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL",
        }).format(valor);
    }

    const canvasComposicao = document.getElementById("grafico-composicao");
    if (canvasComposicao && dados.composicaoCpu.length > 0) {
        new Chart(canvasComposicao, {
            type: "doughnut",
            data: {
                labels: dados.composicaoCpu.map((parte) => parte.grupo),
                datasets: [
                    {
                        data: dados.composicaoCpu.map((parte) => parte.valor),
                        backgroundColor: ["#2f5d8a", "#5b9bd5", "#9dc3e6"],
                    },
                ],
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (contexto) => `${contexto.label}: ${formatarMoeda(contexto.raw)}`,
                        },
                    },
                },
            },
        });
    }

    const canvasCurvaS = document.getElementById("grafico-curva-s");
    if (canvasCurvaS && dados.curvaS.length > 0) {
        new Chart(canvasCurvaS, {
            type: "line",
            data: {
                labels: dados.curvaS.map((ponto) => ponto.competencia),
                datasets: [
                    {
                        label: "Acumulado planejado",
                        data: dados.curvaS.map((ponto) => ponto.acumulado),
                        borderColor: "#2f5d8a",
                        backgroundColor: "rgba(47, 93, 138, 0.15)",
                        fill: true,
                        tension: 0.3,
                    },
                ],
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (contexto) => formatarMoeda(contexto.raw),
                        },
                    },
                },
                scales: {
                    y: {
                        ticks: {
                            callback: (valor) => formatarMoeda(valor),
                        },
                    },
                },
            },
        });
    }
})();
