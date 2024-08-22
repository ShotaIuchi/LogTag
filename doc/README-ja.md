# LogTag

LogTag は、ログメッセージにタグを追加するためのツールです。このスクリプトは、指定されたファイルからログメッセージを読み込み、タグを追加し、必要に応じてソートおよび重複削除を行います。

## 特徴

- 複数のログファイルを結合
- ログメッセージにタグを追加
- ログメッセージをソート
- 重複したログメッセージを削除
- 設定ファイルによる柔軟なカスタマイズ

## インストール

### PyPI からのインストール

**TODO:** このパッケージはまだ PyPI に登録されていません。

```sh
pip install logtag
```

### ローカルでのインストール

このスクリプトをローカルでインストールするには、以下のコマンドを使用します。

```sh
pip install -e .
```

## 使い方

以下のようにスクリプトを実行します。

```sh
python logtag.py -f [ログファイル1] [ログファイル2] ... -o [出力ファイル] [オプション]
```

### オプション

- `-f`, `--file`: タグを追加するログファイルを指定します。複数のファイルを指定できます。
- `-o`, `--out`: 出力ファイルを指定します。指定しない場合、標準出力に表示されます。
- `-s`, `--sort`: ログメッセージをソートします。
- `-u`, `--uniq`: 重複するログメッセージを削除します。
- `--config`: 設定ファイルを指定します。

## 設定ファイル

設定ファイルは JSON 形式で、以下のように構成されます。

### `config.json`

```json
{
  "space": 20
}
```

- `space`: ログメッセージとタグの間のスペースを指定します。

### タグファイル (`tag.json`)

```json
{
  "ERROR": "エラー",
  "INFO": "情報"
}
```

- ログメッセージ内の特定のキーワードに対応するタグを指定します。

### フィルタファイル (`filter.json`)

```json
{
  "display": ["ERROR", "WARN"]
}
```

- 表示するログメッセージのフィルタを指定します。

## 優先順位

設定ファイルの検索パスは以下の優先順位で決定されます。

1. コマンドラインで指定されたディレクトリ
2. ユーザのホームディレクトリ
3. 現在の作業ディレクトリ
4. スクリプトが存在するディレクトリ

## 例

以下は、ログファイル `log1.txt` と `log2.txt` にタグを追加し、結果を `output.txt` に出力する例です。

```sh
python logtag.py -f log1.txt log2.txt -o output.txt --sort --uniq --config ./config
```

このコマンドは、指定されたログファイルを読み込み、タグを追加し、ソートおよび重複削除を行った結果を `output.txt` に出力します。