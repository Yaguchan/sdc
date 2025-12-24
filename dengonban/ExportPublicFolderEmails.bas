Sub ExportPublicFolderEmails()
    Dim olMail As Outlook.MailItem
    Dim olNamespace As Outlook.NameSpace
    Dim olFolder As Outlook.Folder
    Dim olItems As Outlook.Items
    Dim i As Long
    Dim basePath As String
    Dim currentKey As String
    Dim previousKey As String
    Dim startKey As String, endKey As String
    Dim startDate As Date, endDate As Date
    Dim filter As String
    Dim stream As Object

    ' 保存先フォルダのパス
    basePath = "C:\Users\yaguchi.yk110\OneDrive - 日本テレビ放送網株式会社\デスクトップ\回線運用部\data\mail\"

    ' 開始・終了年月をコード内で指定（例：2025年7月～9月）
    startKey = "202507"
    endKey = "202509"

    ' 日付に変換
    startDate = DateSerial(Left(startKey, 4), Right(startKey, 2), 1)
    endDate = DateSerial(Left(endKey, 4), Right(endKey, 2), 1)
    endDate = DateAdd("m", 1, endDate) ' 終了年月の翌月の1日まで含める

    ' Outlookフィルタ形式で範囲指定
    filter = "[ReceivedTime] >= '" & Format(startDate, "ddddd h:nn AMPM") & "' AND [ReceivedTime] < '" & Format(endDate, "ddddd h:nn AMPM") & "'"

    ' 対象フォルダの取得
    Set olNamespace = Application.GetNamespace("MAPI")
    Set olFolder = olNamespace.GetDefaultFolder(olPublicFoldersAllPublicFolders) _
        .Folders("Starnet").Folders("一般").Folders("技術統括局・回線ｾﾝﾀｰ伝言板")

    ' フィルタを適用して対象メールのみ取得
    Set olItems = olFolder.Items.Restrict(filter)
    olItems.Sort "[ReceivedTime]", True

    previousKey = ""

    ' メール処理ループ
    For i = 1 To olItems.Count
        If TypeName(olItems(i)) = "MailItem" Then
            Set olMail = olItems(i)
            currentKey = Format(olMail.ReceivedTime, "yyyymm")

            ' 年月が変わったら前のファイルを保存・閉じる
            If currentKey <> previousKey Then
                If Not stream Is Nothing Then
                    stream.SaveToFile basePath & "outlook_emails_" & previousKey & ".txt", 2
                    stream.Close
                    Set stream = Nothing
                End If

                ' 新しいストリームを開始（UTF-8）
                Set stream = CreateObject("ADODB.Stream")
                With stream
                    .Type = 2
                    .Charset = "utf-8"
                    .Open
                End With

                previousKey = currentKey
            End If

            ' メール内容を書き込み
            With stream
                .WriteText "件名: " & olMail.Subject & vbLf
                .WriteText "送信者: " & olMail.SenderName & vbLf
                .WriteText "受信日時: " & olMail.ReceivedTime & vbLf
                .WriteText "本文: " & olMail.Body & vbLf
                .WriteText "----------------------------------------" & vbLf
            End With
        End If
    Next i

    ' 最後のファイルを保存・閉じる
    If Not stream Is Nothing Then
        stream.SaveToFile basePath & "outlook_emails_" & previousKey & ".txt", 2
        stream.Close
    End If

    MsgBox "メールを " & startKey & "～" & endKey & " の範囲でUTF-8形式で保存しました！"
End Sub