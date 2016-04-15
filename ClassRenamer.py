__author__ = 'salomon'
'''
Rename the classes name which were confused to file name from .source section

'''
from jeb.api import IScript
from jeb.api.ui import View
from collections import defaultdict

class ClassRenamer(IScript):

    def run(self, j):
        self.instance = j
        self.dex = j.getDex()

        pool = defaultdict(list)

        x = 0
        #ignore invalid source, i.e. "proguard" and other self-defined string
        for i in self.dex.getClassSignatures(True):
            # if len(pool.keys()) == 50:
            #     break;
            cls = self.dex.getClass(i)
            #notice some inner class may share same Source Info
            if cls is None or '$' in i:
                continue

            if len(i)-i.rfind('/') > 4:
                continue
           
		    #modify by salomon
            sourceIdx = cls.getSourceIndex()
            if sourceIdx != -1:
                source = self.dex.getString(sourceIdx)
                # self.instance.print("Log: %s %s %s"%(i, cls, source))
                if source == "" or source.lower() == "proguard" or source.upper() == "RQDSRC" or source == "R.java":
                    continue
                if source.endswith(".java"):
                    source = source[:-5]
                    pool[source].append(i)

        self.instance.print("renaming %d classes"%(len(pool.keys())))
        if len(pool.keys()) <= 2:
            return

        for k, v in pool.iteritems():
            ii = 0
            for origin in v:
                newname = k
                # TODO: class in different packged should't be appended with postfix
                if ii > 0:
                    newname = k + '_Sub' + str(ii)
                ii = ii + 1
                if self.instance.renameClass(origin, newname) :
                    self.instance.print("renaming %s  ->  %s success" % (origin,newname))
                else:
                    self.instance.print("warnning renaming %s  ->  %s failed !" % (origin,newname))
                    newname = k + '_Sub0'
                    self.instance.print("try renaming %s  ->  %s ..." % (origin,newname))
                    if self.instance.renameClass(origin, newname) :
                        self.instance.print("try renaming %s  ->  %s success" % (origin,newname))
                    else:
                        self.instance.print("error renaming %s  ->  %s failed !!!" % (origin,newname))

        self.instance.print("renaming done")

        self.instance.getUI().getView(View.Type.JAVA).refresh()
        self.instance.getUI().getView(View.Type.ASSEMBLY).refresh()
        self.instance.getUI().getView(View.Type.CLASS_HIERARCHY).refresh()
