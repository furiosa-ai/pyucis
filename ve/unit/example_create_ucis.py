
import os
from pyucis import *
from pyucis.scope import Scope

from pyucis.source_info import SourceInfo
from pyucis.test_data import TestData


#* Create a design unit of the given name.
#* Note: this hardcodes INST_ONCE and all code coverage enabled (without
#* extended toggle coverage).
def create_design_unit(
        db,
        duname,
        file,
        line) -> Scope:
    srcinfo = SourceInfo(file, line, 0)
    duscope = ucis_CreateScope(db,
                           None, #/* DUs never have a parent */
                           duname,
                           srcinfo,
                           1, #/* weight */
                           UCIS_VLOG, #/* source language */
                           UCIS_DU_MODULE, #/* scope type */
                           #/* flags: */
                           UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH |
                           UCIS_ENABLED_COND | UCIS_ENABLED_EXPR |
                           UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE |
                           UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
    ucis_SetStringProperty(db,duscope,-1,UCIS_STR_DU_SIGNATURE,"FAKE DU SIGNATURE")
    
    return duscope

#* Create a filehandle from the given file in the current directory
#* (Works on UNIX variants only, because of the reliance on the PWD
#* environment variable.)
def create_filehandle(db, filename):
    pwd = os.getcwd()
    filehandle = ucis_CreateFileHandle(db, filename, pwd)
    return filehandle

#* Create test data. For the most part, this is hardcoded.
def create_testdata(db, ucisdb):
    testdata = TestData(
    UCIS_TESTSTATUS_OK,  #/* teststatus */
    0.0,                 #/* simtime */
    "ns",                #/* timeunit */
    "./",                #/* runcwd */
    0.0,                 #/* cputime */
    "0",                 #/* seed */
    "toolname",          #/* cmd */
    "command arguments", #/* args */
    0,                   #/* compulsory */
    "20110824143300",    #/* date */
    "ucis_user",         #/* username */
    0.0,                 #/* cost */
    "UCIS:Simulator"     #/* toolcategory */
    )

    testnode =  ucis_CreateHistoryNode(
           db,
           None,                #/* no parent since it is the only one */
           "TestLogicalName",   #/* primary key, never NULL */
           ucisdb,              #/* optional physical name at creation */
           UCIS_HISTORYNODE_TEST)  #/* It's a test history node */

    if testnode is not None:
        ucis_SetTestData(db, testnode, testdata)

#* Create instance of the given design design unit.
#* This assumes INST_ONCE
def create_instance(db, instname, parent, duscope):
    return ucis_CreateInstance(db,parent,instname,
                        None, #/* source info: not used */
                        1, #/* weight */
                        UCIS_VLOG, #/* source language */
                        UCIS_INSTANCE, #/* instance of module/architecture */
                        duscope, #/* reference to design unit */
                        UCIS_INST_ONCE) #/* flags */
    
#* Create a statement bin under the given parent, at the given line number,
#* with the given count.
def create_statement(db,
            parent,
            filehandle,
            fileno, #/* 1-referenced wrt DU contributing files */
            line,   #/* 1-referenced wrt file */
            item,   #/* 1-referenced wrt statements starting on the line */
            count):
    #/* UOR name generation */
    name = "#stmt#%d#%d#%d#" % (fileno, line, item)

    coverdata = CoverData(UCIS_STMTBIN, UCIS_IS_32BIT)
#        coverdata.data.int32 = count; /* must be set for 32 bit flag */

    srcinfo = SourceInfo(filehandle, line, 17)        
    
    coverindex = ucis_CreateNextCover(db,parent,
                                  name, #/* name: statements have none */
                                  coverdata,
                                  srcinfo)
    
    ucis_SetIntProperty(db,parent,coverindex,UCIS_INT_STMT_INDEX,item)
    
#* Create enum toggle
#* This hardcodes pretty much everything.
def create_enum_toggle(db, parent):
    toggle = ucis_CreateToggle(db,parent,
                           "t", #/* toggle name */
                           None, #/* canonical name */
                           0, #/* exclusions flags */
                           UCIS_TOGGLE_METRIC_ENUM, #/* metric */
                           UCIS_TOGGLE_TYPE_REG,    #/* type */
                           UCIS_TOGGLE_DIR_INTERNAL) #/* toggle "direction" */
    coverdata = CoverData(UCIS_TOGGLEBIN, UCIS_IS_32BIT)
    # coverdata.data.int32 = 0; /* must be set for 32 bit flag */
    ucis_CreateNextCover(db,toggle,
                         "a", #/* enum name */
                         coverdata,
                         None); #/* no source data */
#        coverdata.data.int32 = 1; /* must be set for 32 bit flag */
    ucis_CreateNextCover(db,toggle,
                         "b", #/* enum name */
                         coverdata,
                         None) #/* no source data */

#* Create a covergroup of the given name under the given parent.
#* This hardcodes the type_options.
def create_covergroup(db,
              parent,
              name,
              filehandle,
              line):
    srcinfo = SourceInfo(filehandle, line, 0)
    cvg = ucis_CreateScope(db,parent,name,
                       srcinfo,
                       1, #/* from type_option.weight */
                       UCIS_VLOG, #/* source language type */
                       UCIS_COVERGROUP,
                       0) #/* flags */
    #/* Hardcoding attribute values for type_options: */
    ucis_SetIntProperty(db,cvg,-1,UCIS_INT_SCOPE_GOAL,100)
    ucis_SetIntProperty(db,cvg,-1,UCIS_INT_CVG_STROBE,0)
    ucis_SetIntProperty(db,cvg,-1,UCIS_INT_CVG_MERGEINSTANCES,1)
    ucis_SetStringProperty(db,cvg,-1,UCIS_STR_COMMENT,"")

    return cvg

# Create a coverpoint of the given name under the given parent.
# This hardcodes the type_options.
def create_coverpoint(
        db,
        parent,
        name,
        filehandle,
        line) ->Scope:
    srcinfo = SourceInfo(filehandle, line, 0)
    cvp = ucis_CreateScope(db, parent, name, srcinfo,
                       1, # from type_option.weight
                       UCIS_VLOG, # source language type
                       UCIS_COVERPOINT,
                       0) # flags 
    #* Hardcoding attribute values to defaults for type_options:
    ucis_SetIntProperty(db,cvp,-1,UCIS_INT_SCOPE_GOAL,100)
    ucis_SetIntProperty(db,cvp,-1,UCIS_INT_CVG_ATLEAST,1)
    ucis_SetStringProperty(db,cvp,-1,UCIS_STR_COMMENT,"")
    
    return cvp

#
# Create a coverpoint bin of the given name, etc., under the given
# coverpoint.
# Note: the right-hand-side value for a bin is the value(s) that can cause
# the bin to increment if sampled.
def create_coverpoint_bin(
        db,
        parent,
        name,
        filehandle,
        line,
        at_least,
        count,
        binrhs):
    coverdata = CoverData(UCIS_CVGBIN, UCIS_IS_32BIT | UCIS_HAS_GOAL | UCIS_HAS_WEIGHT, at_least, 1)
#        coverdata.data.int32 = count;
    srcinfo = SourceInfo(filehandle, line, 0)
    coverindex = ucis_CreateNextCover(db,parent,name, coverdata, srcinfo)
                                  
    # This uses a user-defined attribute, named BINRHS
    attrvalue = AttrValue(UCIS_ATTR_STRING)
#        attrvalue.u.svalue = binrhs;
    ucis_AttrAdd(db, parent, coverindex, "BINRHS", attrvalue);


def create_ucis(db):
    create_testdata(db,"file.ucis")
    filehandle = create_filehandle(db,"test.sv")
    du = create_design_unit(db,"work.top",filehandle,0)
    instance = create_instance(db,"top",None,du)
    create_statement(db,instance, filehandle,1,6,1,17)
    create_statement(db,instance, filehandle,1,8,1,0)
    create_statement(db,instance, filehandle,1,9,2, 365)
    create_enum_toggle(db,instance)
    cvg = create_covergroup(db,instance,"cg",filehandle,3)
    cvp = create_coverpoint(db,cvg,"t",filehandle,4)
    create_coverpoint_bin(db,cvp,"auto[a]",filehandle,4,1,0,"a")
    create_coverpoint_bin(db,cvp,"auto[b]",filehandle,4,1,1,"b")
    print("Writing UCIS file '" + ucisdb + "'")
    ucis_Write(db,ucisdb,None,1,-1)
    ucis_Close(db)    



    