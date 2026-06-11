# telegram_translatebot
## 環境構築方法
### ライブラリインストール
```
pip install python-telegram-bot ollama
ollama pull translategemma:12b
```
### Telegram Bot のプライバシー設定
デフォルトの Telegram Bot は、グループやチャンネル内の自分宛て以外のメッセージを読み取れません。
BotFather にて対象の Bot の設定を開き、Group Privacy を Disable にするか、Bot を追加するチャンネル/グループの管理者（Admin）として追加し、メッセージの読み取り権限を付与してください。
### TelegramへのBot登録と起動の手順
TelegramでBotを動かすためには、Telegramの公式管理アカウントである「BotFather」と会話して、Botの身分証明書となる「APIトークン」を発行してもらう必要があります。

1. BotFatherで新しいBotを作成する
> Telegramアプリで @BotFather を検索し、チャットを開始します（公式のチェックマークがついているアカウントです）。
> チャット画面で /newbot と送信します。
> Botの「名前（表示名）」を決めて送信します（例: 翻訳Bot）。
> Botの「ユーザー名」を決めて送信します。
> 必ず最後が bot で終わる必要があり、世界で一意（重複不可）である必要があります（例: my_translate_ollama_bot）。
> 成功すると、画面に Use this token to access the HTTP API: という文字と一緒に、長い文字列（トークン）が表示されるので、これをコピーして控えておきます。

2. Botのプライバシー設定をオフにする:グループ内メッセージを読み取る設定。
> デフォルトでは、Botは自分宛てのコマンドしか読み取れません。
> チャンネルやグループ内の全テキストを翻訳させるために、この制限を解除します。
> 引き続き @BotFather のチャットで /mybots と送信します。
> リストから先ほど作成したBotのユーザー名を選択します。
> Bot Settings ＞ Group Privacy の順にタップします。
> Turn off をタップして、ステータスを Privacy mode is disabled に変更します。

3. Botをチャンネル（またはグループ）に追加する:管理者として追加。
> Telegramの「チャンネル」にBotを追加する場合、Botは一般メンバーではなく**「管理者（Administrator）」として追加する**必要があります。
> Botを追加したいチャンネルの「設定」または「プロフィール画面」を開きます。
> Administrators（管理者） を開き、Add Admin（管理者の追加） をタップします。
> 検索欄にステップ1で決めたBotの @ユーザー名 を入力し、対象のBotを選択します。権限設定（デフォルトのままでOKですが、「メッセージの投稿(Post Messages)」が有効になっていることを確認）をして保存します。

4. プログラムにトークンを設定して起動する:自宅のマシンで実行。
> 先ほど作成したPythonプログラムに、ステップ1で取得したトークンを渡して実行します。
> セキュリティのため、コードに直接書くのではなく環境変数を使うのがおすすめです。

**Windows (コマンドプロンプト) の場合:**
```
DOSset TELEGRAM_BOT_TOKEN=ここにBotFatherから貰ったトークン
python translatebot.py
```

**Mac / Linux (ターミナル) の場合:**
```
Bashexport TELEGRAM_BOT_TOKEN="ここにBotFatherから貰ったトークン"
python translatebot.py
```
起動後、ターミナルに Bot is running... と表示されれば準備完了です！
