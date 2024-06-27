# Asset Lending Smart Contract

Implementation of smart contract for lending.

## requirements

- algokit >= version 2.0.3
- python >= 3.12.3
- node >= v20.12.2

## commands

### build all using algokit
```shell
algokit compile py contract.py
algokit generate client NTAsssetLending.arc32.json --language typescript --output NTAssetLendingClient.ts
algokit generate client NTAssetLending.arc32.json --language python --output NTAssetLendingClient.py
```

### build all using docker

```shell
docker build . -t algokit-builder
```
 
```shell
docker run -v $(pwd):/src -v $(pwd)/artifacts:/artifacts algokit-builder
```