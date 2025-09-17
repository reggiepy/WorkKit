# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tools.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QStatusBar, QTableView, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 561)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.menulistWidget = QListWidget(self.centralwidget)
        QListWidgetItem(self.menulistWidget)
        self.menulistWidget.setObjectName(u"menulistWidget")
        self.menulistWidget.setMaximumSize(QSize(100, 16777215))
        self.menulistWidget.setStyleSheet(u"QListWidget {\n"
"       border: none;\n"
"       background-color: #f0f0f0;\n"
"}\n"
"QListWidget::item {\n"
"       padding: 10px;\n"
"}\n"
"QListWidget::item:selected {\n"
"       background-color: #87CEFA;\n"
"       color: black;\n"
"}")

        self.horizontalLayout.addWidget(self.menulistWidget)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setEnabled(True)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout = QVBoxLayout(self.page)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.page)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.addInvoicePdfpushButton = QPushButton(self.groupBox)
        self.addInvoicePdfpushButton.setObjectName(u"addInvoicePdfpushButton")

        self.horizontalLayout_2.addWidget(self.addInvoicePdfpushButton)

        self.clearInvoicePdfpushButton = QPushButton(self.groupBox)
        self.clearInvoicePdfpushButton.setObjectName(u"clearInvoicePdfpushButton")

        self.horizontalLayout_2.addWidget(self.clearInvoicePdfpushButton)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.invoicePdfTableView = QTableView(self.groupBox)
        self.invoicePdfTableView.setObjectName(u"invoicePdfTableView")
        self.invoicePdfTableView.setAcceptDrops(True)
        self.invoicePdfTableView.setDragEnabled(True)
        self.invoicePdfTableView.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.invoicePdfTableView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_3.addWidget(self.invoicePdfTableView)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.page)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.addSinglePagePdfpushButton = QPushButton(self.groupBox_2)
        self.addSinglePagePdfpushButton.setObjectName(u"addSinglePagePdfpushButton")

        self.horizontalLayout_3.addWidget(self.addSinglePagePdfpushButton)

        self.clearSinglePagePdfpushButton = QPushButton(self.groupBox_2)
        self.clearSinglePagePdfpushButton.setObjectName(u"clearSinglePagePdfpushButton")

        self.horizontalLayout_3.addWidget(self.clearSinglePagePdfpushButton)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.singlePagePdfTableView = QTableView(self.groupBox_2)
        self.singlePagePdfTableView.setObjectName(u"singlePagePdfTableView")
        self.singlePagePdfTableView.setAcceptDrops(True)
        self.singlePagePdfTableView.setDragEnabled(True)
        self.singlePagePdfTableView.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.singlePagePdfTableView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_4.addWidget(self.singlePagePdfTableView)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.startpushButton = QPushButton(self.page)
        self.startpushButton.setObjectName(u"startpushButton")

        self.gridLayout.addWidget(self.startpushButton, 3, 4, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 3, 1, 1)

        self.outputFileNamelineEdit = QLineEdit(self.page)
        self.outputFileNamelineEdit.setObjectName(u"outputFileNamelineEdit")

        self.gridLayout.addWidget(self.outputFileNamelineEdit, 0, 1, 1, 1)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.outputFilePathlineEdit = QLineEdit(self.page)
        self.outputFilePathlineEdit.setObjectName(u"outputFilePathlineEdit")

        self.gridLayout.addWidget(self.outputFilePathlineEdit, 3, 1, 1, 1)

        self.openExplorercheckBox = QCheckBox(self.page)
        self.openExplorercheckBox.setObjectName(u"openExplorercheckBox")
        self.openExplorercheckBox.setChecked(True)

        self.gridLayout.addWidget(self.openExplorercheckBox, 3, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.stackedWidget.addWidget(self.page)

        self.horizontalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.menulistWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)

        self.menulistWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))

        __sortingEnabled = self.menulistWidget.isSortingEnabled()
        self.menulistWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.menulistWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u62a5\u9500\u5408\u5e76\u53d1\u7968", None));
        self.menulistWidget.setSortingEnabled(__sortingEnabled)

        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u53d1\u7968\uff08\u53cc\u6587\u4ef6\u5408\u6210\u4e00\u9875\uff09", None))
        self.addInvoicePdfpushButton.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u6587\u4ef6", None))
        self.clearInvoicePdfpushButton.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u9664", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u5355\u9875PDF", None))
        self.addSinglePagePdfpushButton.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u6587\u4ef6", None))
        self.clearSinglePagePdfpushButton.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u9664", None))
        self.startpushButton.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u5408\u5e76", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u76ee\u5f55", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u6587\u4ef6\u540d", None))
        self.outputFilePathlineEdit.setText(QCoreApplication.translate("MainWindow", u"C:\\WorkKit", None))
        self.openExplorercheckBox.setText(QCoreApplication.translate("MainWindow", u"\u5408\u5e76\u6587\u4ef6\u540e\u5728\u8d44\u6e90\u7ba1\u7406\u5668\u4e2d\u67e5\u770b\u6587\u4ef6", None))
    # retranslateUi

