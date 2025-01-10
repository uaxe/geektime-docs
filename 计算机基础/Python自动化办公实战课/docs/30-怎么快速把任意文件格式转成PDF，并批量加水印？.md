你好，我是尹会生。

在办公场景中，我们打交道最多的软件，要数Office的办公套件了，功能丰富且强大，使用方便。不过你可能也会发现，我们经常用于文字编辑的Word软件，它使用的docx扩展名的文件无论是在不同操作系统平台、不同的设备上，还是在内容安全性和格式的兼容性上，都没有PDF文件强大。Excel和PowerPoint中的文件也是如此。

例如：你需要把公司的合同范本发给其他公司审阅，为了保证文本不会被随意篡改，往往需要把Word或PowerPoint的文件转换为PDF文件，再通过邮件发给其他公司。而且，随着数字化转型的开始，原本在计算机上正常显示的表格，拿到手机上可能会缺少字体；也可能因为屏幕宽度不同，导致格式无法对齐；还可能会出现无法显示文字等格式问题。

不过这些问题呢，PDF统统可以解决。所以像是商业的条款、合同、产品介绍，既要保证安全，又要确保格式正确，如果你不想限制用户必须要用多宽的显示器，或者必须安装好特定的字体，才能看到你的Word、Excel、PowerPoint里的内容的话，那么使用PDF文件就是非常必要的了。

所以在今天这一讲中，我将带你学习如何把Word、Excel、PowerPoint的默认文件格式批量转换为PDF文件，并教你怎么给PDF文件增加水印，既保证样式美观，又确保文档的安全。

## 将常用办公文件转换为PDF格式

如果你以前遇到过类似转换为PDF文件的需求，那么在你搜索Python的第三方库时，就会发现，将Word、Excel、PowerPoint 的默认文件保存格式转换为PDF的库非常多。由于我要将多种格式的文件转换为PDF，那么为了我就需要使用一个能支持Office所有组件的库，而这个库就是pywin32库。

pywin32库支持了绝大多数的Windows API，因此它只能运行在操作系统是Windows上，当你需要使用pywin32操作Office各个组件时，可以利用pywin32库调用Offcie组件中的VBA实现Office组件的大部分功能。

接下来，我将从pywin32库的安装开始，来为你逐步讲解一下如何把Office组件中的Word、Excel、PowerPoint的默认文件保存格式转换为PDF文件。

虽然你要学习三种不同的软件格式转换为PDF文件，但是它们三个文件格式转换的思路和被调用的函数是相同的，你可以通过对照Word文件转换为PDF来去掌握其他两个软件的文件格式转换代码，来学习自动格式转换，这样学起来会更加轻松。

### 将Word文档转换为PDF

我先以Word为例，来为你讲解一下pywin32库的安装、导入，以及将Word文档进行转换的操作步骤。

由于pywin32是第三方库，所以你要使用pip命令把它安装到你的Windows计算机中。这里需要注意，pywin32的安装包和软件名称不同，而且导入的库名称也和pywin32不同。所以我把pywin32库的安装和导入时，使用的名称写在文档中，供你进行参考：

```
SHELL$ pip3 install pypiwin32
PYTHON> import win32com

```

我们 **用于格式转换的库** 叫做 **“win32com”**，它是pywin32软件的库名称。安装它时，你要使用pypiwin32，作为它的安装包名称来使用。这是第一次接触该库最容易混淆的地方，我建议你在阅读后续内容前，先对“pywin32、pypiwin32、win32com”这三个概念进行区分。

在你正确区分上面三个概念之后，我们就可以开始导入win32com库，并调用VBA脚本，来把Word文档转换为PDF格式了。

为了让你更好地理解win32com库的执行过程，我来为你举个例子。我在"C:\\data"文件夹下有一个Word格式的a.doc文件，现在要将它自动转换为a.pdf文件，并继续存储在该目录中。如果你手动进行格式转换，只是需要以下四个步骤：

1. 进入到C:\\data文件夹；
2. 使用Office的Word组件打开 a.doc文件；
3. 使用“文件另存为”功能，保存为PDF格式，并指定保存目录；
4. 保存并关闭Word文件，退出Word进程。

由于win32com库是调用Word的VBA脚本实现的格式转换功能，因此转换格式的Python代码步骤也和手动操作Word几乎相同，少数不同的地方是因为win32com支持的组件较多，需要指定当前转换采用的VBA脚本为Word文件的脚本。我将Word转换PDF的代码写在下方，供你参考。

```
from win32com import client

def word2pdf(filepath, wordname, pdfname):
    worddir = filepath
    # 指定Word类型
    word = client.DispatchEx("Word.Application")
    # 使用Word软件打开a.doc
    file = word.Documents.Open(f"{worddir}\{wordname}", ReadOnly=1)
    # 文件另存为当前目录下的pdf文件
    file.ExportAsFixedFormat(f"{worddir}\{pdfname}", FileFormat=17， Item=7, CreateBookmarks=0)
    # 关闭文件
    file.Close()
    # 结束word应用程序进程
    word.Quit()

```

我来为你详细解释一下上面这段代码。这段代码中我定义了一个word2pdf()函数，它被Python调用时，会根据自己的参数将word文件的路径、word文件的名称和pdf名称传入参数中。

根据这些参数word2pdf()函数会调用DispatchEx()打开Word程序，再使用Open()函数打开a.doc文件，并使用ExportAsFixedFormat()函数将Word文件另存为PDF文件之后，使用Close()和Quit()关闭a.doc文件并结束Word进程。

由于win32com是用过Word的VBA脚本实现对Word进程行为的控制的，所以它的操作步骤和手动操作非常相似，所以这段代码也非常容易理解。

那在这里我需要提醒你注意两个容易被忽视的问题，第一个是由于win32com库在Windows系统上是直接调用Word进程实现格式转换的，因此你必须为当前的Windows安装Word以及Office的办公组件。那另一个是由于win32com对Word操作的方式是基于Word的VBA脚本，所以你想在转换时为ExportAsFixedFormat()函数增加新的参数，需要参考Office官方网站的文档。

我也将Office官方网站关于Word的VBA脚本所在网页提供给你做参考（ [https://docs.microsoft.com/zh-cn/office/vba/api/word.document.exportasfixedformat](https://docs.microsoft.com/zh-cn/office/vba/api/word.document.exportasfixedformat)）。当你增加新的功能时，可以通过网页的内容来获得更多功能。

### 将Excel表格转换为PDF

在你掌握了如何使用win32com实现Word文档转换为PDF之后，我再来带你实现Excel表格自动转换为PDF的功能，你也可以对比着来学习掌握，同时也注意观察把Excel和Word文件转换为PDF的主要差别。

Excel表格默认保存的文件格式是xls或xlsx，将xls或xlsx格式转换为PDF的步骤和思路与Word文档转换为PDF相同，所以我先把代码提供给你，然后再为你讲解。代码如下：

```
from win32com import client

def excel2pdf(filepath, excelname, pdfname):
    exceldir = filepath
    # 指定Excel类型
    excel = client.DispatchEx("Excel.Application")
    # 使用Excel软件打开a.xls
    file = excel.Workbooks.Open(f"{exceldir}\{excelname}", False)
    # 文件另存为当前目录下的pdf文件
    file.ExportAsFixedFormat(0, f"{excel}dir}\{pdfname}")
    # 关闭文件
    file.Close()
    # 结束excel应用程序进程
    excel.Quit()

```

对比word2pdf()和excel2pdf()，你会发现实现的基本逻辑是相同的，但是在实现Excel转换上，有两个主要函数的参数不同。

1. DispatchEx()函数的参数，这里使用了“Excel.Application”字符串作为该函数的参数，“Excel.Application”作为DispatchEx()参数的目的是，让pywin32库启动Excel进程，并让它读取“a.xls”文件。
2. ExportAsFixedFormat函数的第一个参数从pdf路径变为保存的类型，你可以参考 [Office的Excel VBA官方文档](https://docs.microsoft.com/zh-cn/office/vba/api/excel.workbook.exportasfixedformat)，从中学习函数的每个参数。

### 将PowerPoint幻灯片转换为PDF

在你学习了Word文档和Excel表格转换PDF文件的基础上，我再来带你你对比学习一下如何将PowerPoint的默认保存文件ppt格式转换为PDF。参考word2pdf()和excel2pdf()两个函数，我直接将PowerPoint的幻灯片转换PDF文件的代码提供给你，你可以通过官方文档( [https://docs.microsoft.com/zh-cn/office/vba/api/powerpoint.presentation.exportasfixedformat](https://docs.microsoft.com/zh-cn/office/vba/api/powerpoint.presentation.exportasfixedformat))，来试着分析ppt2pdf()函数的参数和函数里的每行代码。

```
from win32com import client

def ppt2pdf(filepath, pptname, pdfname):
    pptdir = filepath
    # 指定PPT类型
    ppt = client.DispatchEx("PowerPoint.Application")
    # 使用ppt软件打开a.ppt
    file = ppt.Presentations.Open(f"{pptdir}\{pptname}", False)
    # 文件另存为当前目录下的pdf文件
    file.ExportAsFixedFormat(f"{pptdir}\{pdfname}")
    # 关闭文件
    file.Close()
    # 结束excel应用程序进程
    excel.Quit()

```

显而易见，PowerPoint幻灯片转换为PDF文件的代码逻辑和word2pdf()和excel2pdf()函数的逻辑完全相同，只有两处有所不同，一个是DispatchEx()的参数为“PowerPoint.Application”，它的功能是让win32com库打开PowerPoint进程。另一个是ppt.Presentations.Open()打开的对象不同，它打开的是每一页的PPT，而Excel打开的是每个sheet对象。

以上就是如何将Office组件的Word、Excel与PowerPoint的默认保存文件格式转换为PDF格式。在转换之后，我们经常为了保护知识产权，或者增强文件的安全性，需要给PDF文件增加水印。所以接下来我就带你学习如何通过增加水印提高PDF文件的安全性。

## 提高PDF文件的安全性

安全性包括很多方面，比如为文档增加密码，从而增强保密性；也可以为文档增加水印，提升它的不可伪造性。如果你对前面课程熟悉的话，就能联想到我们在第27节课讲过，可以利用我们自动压缩的方式来给文件增加密码，所以我在今天这节课，主要以如何给PDF文件增加水印。

### 为PDF增加水印

为PDF文件增加水印，你可以通过pyPDF2库来实现。使用pyPDF2库的好处是，你不需要在当前计算机上安装任何PDF编辑器，就可以给PDF文件增加水印。

基于pyPDF2库来给PDF文件增加水印的原理是，把只带有水印的PDF文件，和需要增加水印的PDF文件合并即可。根据这一原理，你大概就能想到增加水印的步骤了。主要有三步，分别是：准备水印文件、安装pyPDF2库以及合并两个PDF文件。

老规矩，我们还是先从准备水印文件开始学习。带有水印的PDF文件，可以使用Word软件来生成。具体操作方法是：通过Word的“设计”-“水印”功能，来定制你自己的水印文件，接着再把它另存为PDF格式，之后这个带有水印的文件你就可以反复使用了。

接下来是安装pyPDF2的第三方库。由于它的安装包和软件同名，所以可以使用pip命令直接安装。安装后，我需要通过该库实现PDF文件的读写。我使用了这个库用于读写PDF文件的“PdfFileReader, PdfFileWriter”两个包，导入的代码如下：

```
from PyPDF2 import PdfFileReader, PdfFileWriter

```

第三步，也是最重要的一步， **合并两个PDF文件**。合并文件需要使用 **pyPDF2库的mergePage()函数** 实现。在实际工作中，我们通常需要给PDF文件的每一页都增加水印，此时我们需要使用for循环来迭代每一页，迭代之后，再把合并好的PDF文件保存为新的文件即可。

我把合并两个PDF文件的代码写在下面，然后再带你分析整个合并流程。

```
from PyPDF2 import PdfFileReader, PdfFileWriter

def watermark(pdfWithoutWatermark, watermarkfile, pdfWithWatermark):

    # 准备合并后的文件对象
    pdfWriter = PdfFileWriter()

    # 打开水印文件
    with open(watermarkfile, 'rb') as f:
        watermarkpage = PdfFileReader(f, strict=False)

        # 打开需要增加水印的文件
        with open(pdfWithoutWatermark, 'rb') as f:
            pdf_file = PdfFileReader(f, strict=False)

            for i in range(pdf_file.getNumPages()):
                # 从第一页开始处理
                page = pdf_file.getPage(i)
                # 合并水印和当前页
                page.mergePage(watermarkpage.getPage(0))
                # 将合并后的PDF文件写入新的文件
                pdfWriter.addPage(page)

    # 写入新的PDF文件
    with open(pdfWithWatermark, "wb") as f:
        pdfWriter.write(f)

```

在这段代码中，我定义了函数watermark()，用来实现为PDF文件增加水印的功能。它的实现思路是先读取水印PDF文件，再把水印PDF文件与需要增加水印的文件的每一页进行合并。合并之后，我通过使用PdfFileWriter()类，产生了新的对象pdfWriter，并将合并后产生的新PDF文件存储在pdfWriter对象中。最后，在所有页处理完成后，将合并后的PDF文件保存到“pdfWithWatermark”对象指向的文件中。

在这段代码中你需要注意的是，我使用了“with方式”打开了文件，在文件处理完成前如果关闭文件的化，会出现“file close error”异常。因此你需要注意代码第9、13行的with缩进，而写入新的文件可以在水印PDF文件和要增加水印的文件关闭后进行，所以代码的第25行“with语句”缩进可以在它上面的两个with代码块以外进行编写。

为了让你更直接地感知到增加水印后的结果，我把增加水印后的结果贴在下方，供你参考。

![](https://static001.geekbang.org/resource/image/55/19/55c66ba8ec59yy19cd8b83406eb96f19.png?wh=698x675)

以上就是我使用PyPDF2库为PDF增加水印的全部流程。不过除了增加水印外，你还能使用pdfWriter对象，来实现很多实用的功能，比如为PDF文件设置密码、插入新的页面、旋转PDF页面等等。

此外，由于pyPDF2库封装得非常好，所以它的调用很简单，你只需一个函数就能实现我刚才提到的这些功能了。我将pyPDF2库的官方文档链接（ [https://pythonhosted.org/PyPDF2/](https://pythonhosted.org/PyPDF2/)）贴在这里，当你需要操作PDF文件实现其他功能时，可以参考官方文档中PdfFileWriter()函数的参数，为不同的功能增加相应参数即可。

## 小结

最后，我来为你总结一下今天的主要内容。在本讲中，我为你讲解了如何通过pywin32库把Offce组件常用的doc、docx、xls、xlsx、ppt、pptx等文件转换为PDF文件格式的通用方法。这个通用的方法就是 **通过pywin32库的COM编程接口，调用VBA脚本实现格式的转换。**

你学会了pywin32库之后，除了能把这些办公文件转换为PDF文件外，还能对Office组件中的任意一个软件进行 **常见功能的调用**，因为\*\*pywin32调用的VBA脚本和Office宏的脚本是完全相同的。

我在本讲中除了为你讲解了pywin32库外，还讲解了pyPDF2库。pyPDF2库能够在你将文件转换为PDF之后，还能对PDF的格式和内容进行微调，让你的PDF文件批量处理能达到手动处理的文件精细程度。

最后，你还可以把PDF文件和上一讲中的自动收发邮件，以及我们学习过的Word自动处理相结合，把PDF格式的合同作为邮件附件进行文件的自动生成和邮件的自动发送。

## 思考题

按照惯例，我来为你留一道思考题。如果在一个文件夹中既有Word文件，又有PowerPoint文件，你该如何将文件夹中的这些类型的文件，批量转换为PDF文件呢？