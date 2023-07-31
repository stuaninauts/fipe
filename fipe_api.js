/*
 * TODO:
 * Testar quais parametros sao realmente necessarios nas api calls
*/

async function fetchTabelaReferencia() {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarTabelaDeReferencia", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;

}

async function fetchMarcas(ref=1) {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarMarcas", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "body": `codigoTabelaReferencia=${ref}&codigoTipoVeiculo=1`,
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;
}

async function fetchModelos(ref=1, marca=1) {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarModelos", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "body": `codigoTipoVeiculo=1&codigoTabelaReferencia=${ref}&codigoModelo=&codigoMarca=${marca}&ano=&codigoTipoCombustivel=&anoModelo=&modeloCodigoExterno=`,
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;
}

async function fetchAnoModelo(ref=1, marca=1, modelo=1) {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarAnoModelo", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "body": `codigoTipoVeiculo=1&codigoTabelaReferencia=${ref}&codigoModelo=${modelo}&codigoMarca=${marca}&ano=&codigoTipoCombustivel=&anoModelo=&modeloCodigoExterno=`,
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;
}

async function fetchModeloAtravesdoAno(ref=1, marca=1, ano='2023-1') {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarModelosAtravesDoAno", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "body": `codigoTipoVeiculo=1&codigoTabelaReferencia=${ref}&codigoModelo=&codigoMarca=${marca}&ano=${ano}&codigoTipoCombustivel=${ano.split('-')[1]}&anoModelo=${ano.split('-')[0]}&modeloCodigoExterno=`,
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;
}

async function fetchCarro(ref=1, marca=1, modelo=1, ano='2023-1') {
    let response = await fetch("https://veiculos.fipe.org.br/api/veiculos/ConsultarValorComTodosParametros", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": "https://veiculos.fipe.org.br/",
        "body": `codigoTabelaReferencia=${ref}&codigoMarca=${marca}&codigoModelo=${modelo}&codigoTipoVeiculo=1&anoModelo=${ano.split('-')[0]}&codigoTipoCombustivel=${ano.split('-')[1]}&tipoVeiculo=carro&modeloCodigoExterno=&tipoConsulta=tradicional`,
        "method": "POST",
        "mode": "cors"
    });
    let jsonData = await response.json();
    return jsonData;
}

async function main() {
    
    referencias = await fetchTabelaReferencia();
    marcas = await fetchMarcas(299);
    console.log(marcas)
    modelos = await fetchModelos(299, 7);
    ano_modelo = await fetchAnoModelo(299, 7, 6146);
    carros_do_ano = await fetchModeloAtravesdoAno(299, 6, "2015-1");
    console.log(carros_do_ano);
    carro = await fetchCarro(299, 7, 6146, "2015-1");
    console.log(carro);

}
main();