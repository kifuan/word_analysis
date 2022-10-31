# 分析QQ聊天记录词频!

用来分析你和裙友/好友聊天记录的词频。

## Usage

1. `git clone` 代码，这个我不说了。

2. 安装所需依赖：

   ```bash
   > pip install -r requirements.txt
   ```

3. 找到你想要迫害的群/好友，按照如下步骤操作：

   ![Step 1 2](screenshots/1.png)

   ![Step 3 4](screenshots/2.png)

   ![Step 5 6](screenshots/3.png)

   最好在这里把文件名改一改，改成英文的，比较稳妥。

4. 把导出的文件和 `git clone` 下的代码放到同一目录，然后在控制台输入类似于这样的命令：

   ```bash
   > python main.py -f test.txt -m group -q 111222333 -l 30
   > python main.py -f test.txt -w CERTAIN_WORD -m group -l 5
   ```

   + `-f, --file` 是你保存的**文件名**
   + `-m, --mode` 
      + 如果是群聊就是 `group`
      + 如果是好友就是 `friend`
   + `-q, --qid`
      + 如果是好友模式，你需要输入文件里显示的**用户名**
      + 如果是群聊模式，你需要输入这个人的**QQ号**
   + `-l, --limit` 是筛选出前多少个
   + `-w, --word` 看谁说这个词的频率高，当它有值时无需设置 `qid`

