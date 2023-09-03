/*
 * USAGE:
 *  $ node fipe_api.js [dir] [err_filename] [refs...]
 *
 * IMPORTANT:
 *  dir must already exist
 * 
 * OUTPUT:
 *  dir/
 *      err_file    - Contains the failed API calls
 *      ref0.csv
 *      ref1.csv
 *      ...
 *      refn.csv
 * 
 *  refn.csv
 *      ano_ref, mes_ref, marca, modelo, ano_fab, valor, combustivel, codigo_fipe
 * 
 * 
*/

const fs = require('fs');

async function fetchTabelaReferencia(err_fn) {
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
    if (response.status !== 200) {
        await err_fn("response status !== 200 when fetching TabelaReferencia");
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn("could not convert response to json when fetching TabelaReferencia");
        return undefined;
    }

}

async function fetchMarcas(ref=1, err_fn) {
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
    if (response.status !== 200) {
        await err_fn(`response status !== 200 with fetchMarcas ${ref}`);
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn(`could not convert to json with fetchMarcas ${ref}`);
        return undefined;
    }
}

async function fetchModelos(ref=1, marca=1, err_fn) {
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
    if (response.status !== 200) {
        await err_fn(`response status !== 200 with fetchModelos ${ref} ${marca}`);
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn(`could not convert to json with fetchModelos ${ref} ${marca}`);
        return undefined;
    }
}

async function fetchAnoModelo(ref=1, marca=1, modelo=1, err_fn) {
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
    if (response.status !== 200) {
        await err_fn(`response status !== 200 with fetchAnoModelo ${ref} ${marca} ${modelo}`);
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn(`could not convert to json with fetchAnoModelo ${ref} ${marca} ${modelo}`);
        return undefined;
    }
}

async function fetchModeloAtravesdoAno(ref=1, marca=1, ano='2023-1', err_fn) {
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
    if (response.status !== 200) {
        await err_fn(`response status !== 200 with fetchModeloAtravesdoAno with ${ref} ${marca} ${ano}`);
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn(`could not convert to json with fetchModeloAtravesdoAno with ${ref} ${marca} ${ano}`);
        return undefined;
    }
}

async function fetchCarro(ref=1, marca=1, modelo=1, ano='2023-1', err_fn) {
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
    if (response.status !== 200) {
        await err_fn(`response status !== 200 with fetchCarro ${ref} ${marca} ${modelo} ${ano}`);
        return undefined;
    }
    try {
        let jsonData = await response.json();
        return jsonData;
    } catch {
        await err_fn(`could not convert to json with fetchCarro ${ref} ${marca} ${modelo} ${ano}`);
        return undefined;
    }
}


async function main(dir, err_filename, refs = []) {
    
    // Add checks for
        // dir existence
        // err_filename exists or must be created?

    async function handleError(msg) {
        console.log(`[ERROR] ${msg}`);
        fs.writeFileSync(err_filename, msg, {flag: 'a'});
    }

    // Add column to csv
    async function writeToFile(filename, row) {
        try {
            fs.writeFileSync(`${dir}/${filename}`, row, {flag: 'a'});
        } catch {
            await handleError(`Could add ${row} to ${filename}`);
        }


    }

    const csv_header = "ano_ref;mes_ref;marca;modelo;ano_fab;valor;combustivel;codigo_fipe\n"
    const ref_lookup = await fetchTabelaReferencia(handleError);

    for (const ref of refs) {
        let refInfo = ref_lookup.find((e) => e['Codigo'] === ref);
        if (!refInfo) {
            await handleError(`Invalid ref ${ref}`);
            continue;
        }
        let filename = refInfo['Mes'].replace('/', '-');
        await writeToFile(filename, csv_header);
        let refMes = refInfo['Mes'].split('/')[0]
        let refAno = refInfo['Mes'].split('/')[1].trim();

        let codigoRef = ref;
        let marcas = await fetchMarcas(codigoRef, handleError);
        if (!marcas)
            continue;

        for (const marca of marcas) {
            let labelMarca = marca['Label'].trim();
            let codigoMarca = Number(marca['Value']);
            let modelos = await fetchModelos(codigoRef, codigoMarca, handleError);
            if (!modelos)
                continue;

            for (const modelo of modelos['Modelos']) {
                let labelModelo = modelo['Label'].trim();
                let codigoModelo = modelo['Value'];
                let anos = await fetchAnoModelo(codigoRef, codigoMarca, codigoModelo, handleError);
                if (!anos)
                    continue;
                
                for (const ano of anos) {
                    let codigoAno = ano['Value'];
                    let carro = await fetchCarro(codigoRef, codigoMarca, codigoModelo, codigoAno, handleError);
                    if (!carro)
                        continue;
                    
                    let carroValor = carro['Valor'];
                    let carroCombustivel = carro['Combustivel'];
                    let carroCodigoFipe = carro['CodigoFipe'];
                    let carroAno = codigoAno.split('-')[0]
                    let row = `${refAno};${refMes};${labelMarca};${labelModelo};${carroAno};${carroValor};${carroCombustivel};${carroCodigoFipe}\n`;
                    await writeToFile(filename, row);
                }

            }

        }
    }


}

main(process.argv[2], process.argv[3], process.argv.slice(4).map(e => Number(e)));
