#!/bin/bash

set -ex

export GOPATH=$HOME/my-go-path # Edit this as you like.

go get github.com/ethereum/go-ethereum
cd "$GOPATH/src/github.com/ethereum/go-ethereum"

git checkout develop

cd ./cmd/ethtest
go install

