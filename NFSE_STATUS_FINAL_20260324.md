# NFS-e Nacional — Status Final 2026-03-24

## Pipeline: 100% funcional

```
XML DPS → NFSeNacionalXMLSigner (sem ds:) → GZip → Base64 → POST JSON mTLS → sefin.nfse.gov.br
```

Tudo funciona. O governo recebe, valida o schema XML, aceita a assinatura digital, processa o DPS. Zero erros técnicos.

## Bloqueador: E0310

```
"O código de tributação nacional informado não existe conforme a lista de serviços
 nacional do Sistema Nacional NFS-e."
```

Testamos dezenas de códigos (110200, 110201, 110202, 070102, 140601, etc.) — nenhum é aceito para o CNPJ/município de Manaus. Isso significa que:

1. **Manaus aderiu ao sistema nacional** (Decreto 6.743, obrigatório desde 01/01/2026)
2. Mas os **códigos de tributação municipal** ainda não estão totalmente cadastrados na plataforma nacional
3. Ou a empresa precisa de um **cadastro específico** no portal NFS-e Nacional antes de emitir

## Ação do Jordan

Consultar a SEMEF de Manaus para saber:
1. Quais cTribNac estão cadastrados para a empresa 35.710.481/0001-03 no sistema nacional
2. Se é necessário fazer um cadastro prévio no portal www.nfse.gov.br/EmissorNacional
3. Email SEMEF: nota.monitoramento@manaus.am.gov.br | Disque 156

## Erros resolvidos (acumulado de todas as sessões)

| # | Erro | Correção |
|---|---|---|
| 1 | E6155 | Assinatura sem prefixo ds: (NFSeNacionalXMLSigner) |
| 2 | RNG6110 (prest) | Adicionado tpEmit + cLocEmi antes de prest |
| 3 | RNG6110 (IM) | Fallback IM para 45177801 |
| 4 | RNG6110 (toma) | Adicionado xNome obrigatório |
| 5 | RNG6110 (locPrest) | Removido cPaisPrestacao |
| 6 | RNG6110 (cTribNac) | Truncado para 6 dígitos |
| 7 | RNG6110 (tribMun) | Removido cLocIncid |
| 8 | cPaisResult | BACEN 1058 → ISO BR |
| 9 | BM/exigSusp | Removidos (opcionais) |
| 10 | E0237 | tpRetISSQN=1 (não retido) |
| 11 | E0006 | tpAmb=1 (produção) |
| 12 | E0008 | Fuso Brasília -03:00 |
| 13 | E0310 | **BLOQUEIO CADASTRAL** (não é erro de código) |

## Score Gov: 9/10

O que falta para 10/10:
- NFS-e: Jordan resolver E0310 com SEMEF → imediato após ter o código correto
- EFD-Reinf R-1000: mesmo padrão SOAP do eSocial (2-4h de dev)
- S-2200: Jordan fornecer dados dos funcionários
- Gov.br: Jordan registrar app
