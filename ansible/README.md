# ansible

Pi 4のセットアップ自動化（WiFi AP + アプリケーション）

## Prerequisites

1. `inventory/hosts.yaml` の `USER_NAME` / `PASSWORD` / `HOST_NAME` を実際の値に変更
2. `group_vars/all.yml` で AP の SSID・パスワード・IP を確認・変更

## Full Setup

```sh
ansible-playbook -i inventory/hosts.yaml setup-all.yml
```

## Individual Components

```sh
ansible-playbook -i inventory/hosts.yaml setup-access-point.yml
```

```sh
ansible-playbook -i inventory/hosts.yaml setup-app.yml
```

## Reset
> AP プロファイルと全サービス・アプリケーションを削除し、Pi 4 をデフォルト状態にする。
```sh
ansible-playbook -i inventory/hosts.yaml reset.yml
```
