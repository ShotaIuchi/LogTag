# LogTag

LogTag は、ログメッセージにタグを追加するためのツールです。指定されたファイルからログメッセージを読み込み、タグを追加し、必要に応じてソートや重複削除を行います。

## 特徴

- 複数のログファイルを結合
- ログメッセージにタグを追加
- ログメッセージをソート
- 重複するログメッセージを削除
- 設定ファイルによる柔軟なカスタマイズ
- タグのマッチングに正規表現対応

## インストール

### PyPI からのインストール

このパッケージはまだ PyPI に登録されていません。

```sh
pip install logtag
```

### ローカルインストール

このスクリプトをローカルにインストールするには、以下のコマンドを使用してください。

```sh
pip install -e .
```

## 使用方法

次のようにスクリプトを実行します。

```sh
logtag [files] -o [output_file] [options]
```

### 引数

- `files`: 処理する 1 つ以上のログファイルを指定します。ワイルドカードも使用可能です（例：`*.txt`で全ての`.txt`ファイルにマッチ）。

### オプション

- `-o`, `--out`: 指定ファイルに結果を出力します。
- `-s`, `--sort`: ログメッセージをソートします。
- `-u`, `--uniq`: !!!廃止予定!!! タグ付けしたメッセージのみを表示します。
- `-f`, `--filter`: タグ付けしたメッセージのみを表示します。
- `-m`, `--merge`: ログメッセージを結合します。
- `--hidden`: ログメッセージのコンソール出力しません。
- `--config`: カスタム設定ディレクトリを指定します。
- `--config-first-directory-tag`: タグファイルのカスタム設定を、最初に見つけたディレクトリのみで読み込みます。
- `--category`: 1 つ以上のタグカテゴリを指定し、ログメッセージをフィルタリングします。指定しない場合、全てのカテゴリが使用されます。
- `--stop-first-tag`: 1 行に対するタグ付けを最初のタグがヒットした時点で終了します。
- `--stop-first-category`: 1 行に対するタグ付けを最初のタグがヒットした時点で終了します。
- `--table-theme`: テーブルのテーマを変更します。
  - テーマ種別: https://github.com/gregbanks/python-tabulate?tab=readme-ov-file#table-format

## 設定ファイルの概要

このシステムの設定ファイルは YAML 形式で構成されており、一般設定ファイル（`config.yaml`）とカテゴリ別のログタグファイル（`lotgag/<number>-<category>.yaml`）の 2 つの部分で構成されています。

### `config.yaml`

```yaml
# ログ出力に表示する列の設定
column:
  - name: TAG
    display: TAG
    enable: true
  - name: CATEGORY
    display: CATEGORY
    enable: true
  - name: FILE
    display: LOG-FILE
    enable: true
  - name: LOG
    display: LOG
    enable: true

# ログのフィルタリングに使用するタグカテゴリを有効化
# カテゴリは "<tag>-<subtag>" の形式で指定
category:
  # - "default"
  # - "android"
  # - "android-kernel"
  # - "etc..."
```

- **`column`**: ログ出力に表示する列を定義します。表示の有無や表示名も設定できます。
  - `name`: 列の内部名。
  - `display`: ログ出力に表示される列の名前。
  - `enable`: 列を表示するかどうか（`true`で表示、`false`で非表示）。
- **`category`**: ログタグカテゴリをフィルタリングのために定義します。必要に応じてカテゴリを追加・削除できます。すべてのカテゴリを使用する場合は、このセクションを空のままにします。

### タグファイル (`lotgag/<number>-<category>.yaml`)

各カテゴリには独自のログタグ設定ファイルがあり、次のように構成されます：

```yaml
- keyword: hoge-log
  message: hoge-message
- keyword: fuga.*log
  message: fuga-message
  regex: true
```

- **`<category>`**: ファイル名はカテゴリ名に対応しており、各ファイルにはそのカテゴリに属する複数のキーワードを定義できます。
- **`keyword`**: マッチする特定のログキーワード。
- **`message`**: キーワードの説明。
- **`regex`**: キーワードを正規表現として解釈するかどうか（`true`で正規表現として解釈）。省略した場合は文字列として扱われます。

### ディレクトリ構造

ツールは以下の優先順位で設定ファイルを検索します。

1. コマンドラインで指定されたディレクトリ
2. カレントワーキングディレクトリ
3. ユーザーのホームディレクトリ
4. スクリプトが配置されているディレクトリ

## 使用例

次の例では、ログファイルにタグを追加し、ログメッセージをソートし、重複を削除し、結果を`output.txt`に出力します。ワイルドカード（`*.txt`）を使用して複数のファイルをマッチさせることが可能です。

```sh
$ logtag *.txt -o output.txt --sort --filter --config ./config
```

```sh
$ python logtag.py *.txt -o output.txt --sort --filter --config ./config
```

このコマンドは、現在のディレクトリ内のすべての `.txt` ファイルを読み込み、タグを追加し、ログメッセージをソートして重複を削除し、結果を `output.txt` に出力します。`--config` オプションでカスタム設定ディレクトリを指定すると、ツールはそのディレクトリ内の `config.yaml` および `logtag.yaml` を参照します。
