import sys
import os

# Automata's States
initalState = 0
createState = 1
attributeState = 2
constraintState = 3
endOfFileState = 5

# Processing variables
actualState = 0
actualFileIndex = 0;
actualLine = ''
actualTable = ''
tables = []
attributesInTable = {}
foreingKeysInTable = {}
primaryKeyInTable = {}


# To treat the SQL Sintax
constraintStatements = ['PRIMARY','INDEX','CONSTRAINT','FOREIGN','REFERENCES','ON']
primaryKeyStatement = 'PRIMARY KEY'
createStatement = 'CREATE TABLE'
openParentesis = '('
closeParentesis = ')'
foreingKeyStatement = 'FOREIGN KEY'
referencesStatement = 'REFERENCES'

# To create the Java class
classHeader = 'public final class'
startOfBlock = '{'
endOfBlock = '}'
endOfLine = ';'
publicStatement = 'public'
classEntryDefinition = 'public static abstract class'
classEntryInterface = 'implements BaseColumns'
entryDefinition = 'public static final String'


def currentLine():
	line = fileByLines[actualFileIndex].upper()
	line = line.replace('`', '')
	
	return line

def generateDBHelper():
	print 'package hunabsys.classifiertest;'
	print ''
	#print 'import hunabsys.classifiertest.entities'
	print 'import android.content.Context;'
	print 'import android.content.ContentValues;'
	print 'import android.database.sqlite.SQLiteDatabase;'
	print 'import android.database.sqlite.SQLiteOpenHelper;'
	print ''
	print 'public class DatabaseHelper extends SQLiteOpenHelper {'
	print ' '
	print '\t private static final String DATABASE_NAME = "contactsManager";'
	print '\t private static final String LOG = "DatabaseHelper";'
	print '\t private static final int DATABASE_VERSION = 1;'


	# Print each table and its attributes
	print '\t  '
	for table in tables:
		print '\t private static final String TABLE_' + table + ' = "' + table + '";'
		if not attributesInTable.has_key(table): continue

		for attrSQL in attributesInTable[table].split('$'):
			attr = attrSQL.split(' ')[0]
			print '\t private static final String '  + table + '_' + attr + '="' + attr + '";'
			
		tableDef = attributesInTable[table].replace('$', ',') + ' '
		createTableVar = '\t private static final String CREATE_TABLE_' + table + ' = "'
		createTableVar += 'CREATE TABLE ' + table + '( ' + tableDef

		if primaryKeyInTable.has_key(table): 
			createTableVar += ',' + primaryKeyStatement + '(' + primaryKeyInTable[table] + ')'


		if foreingKeysInTable.has_key(table):
			for fkSQL in foreingKeysInTable[table].split('$'):
				fk = fkSQL.split('.')

				createTableVar += ',' + 'FOREIGN KEY (' + fk[0] +') '
				createTableVar += 'REFERENCES ' + fk[1] + '(' + fk[2] + ')'
			
		createTableVar += ')";'

		print createTableVar
		print '\t '



	# prints the constructor and other methodsclear
	print '\t public DatabaseHelper(Context context) {'
	print '\t \tsuper(context, DATABASE_NAME, null, DATABASE_VERSION);'
	print '\t }'
	print '\t '
	print '\t public void closeDB() {'
	print '\t \t SQLiteDatabase db = this.getReadableDatabase();'
	print '\t \t if (db != null && db.isOpen())'
	print '\t \t \tdb.close();'
	print '\t }'
	print '\t '
	print '\t @Override'
	print '\t public void onCreate(SQLiteDatabase db) {'
	for table in tables:
		print '\t \t db.execSQL(CREATE_TABLE_' + table + ');'
	print '\t }'

	print '\t '
	print '\t @Override'
	print '\t public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {'
	for table in tables:
		print '\t \t db.execSQL("DROP TABLE IF EXISTS " + CREATE_TABLE_' + table +');'

	print '\t \t onCreate(db);'
	print '\t }' 
	print '}' 

def isEndOfFileState(state):
	result = False
	if state == endOfFileState:
		result = True

	return result

def isInitialState(state):
	result = False

	if state == initalState:
		result = True

	return result

def isCreateState(state):
	result = False

	if state == createState:
		result = True

	return result

def isAttributeState(state):
	result = False

	if state == attributeState:
		result = True

	return result

def isConstraintState(state):
	result = False

	if state == constraintState:
		result = True

	return result

def isTableDeclarationEnd(statement):
	isEnd = False

	numberOfCloseParentesis = statement.count(closeParentesis)
	numberOfOpenParentesis = statement.count(openParentesis)
	
	if numberOfOpenParentesis < numberOfCloseParentesis: 
		isEnd = True
	
	return isEnd

def isEndOfFile():
	result = False
	if actualFileIndex >= numLines:
		result = True

	return result

def isPrimaryKeyConstraint(statement):
	result = False

	if primaryKeyStatement in statement:
		result = True

	return result

def isForeignKeyConstraint(statement):
	result = False

	if foreingKeyStatement in statement:
		result = True

	return result

def hasCreateStament(statement):
	result = False

	if createStatement in statement:
		result = True

	return result

def hasConstraint(statement):
	result = False
	statements = statement.split(' ')

	for si in statements:
		for constraint in constraintStatements:
			if si == constraint: 
				result = True
				break

	return result

def getTableName(statement):
	tableName = statement
	tableName = tableName.replace('`', '')
	tableName = tableName.replace(openParentesis, '')
	tableName = tableName.replace(closeParentesis, '')
	tableName = tableName.split('.')[1]
	tableName = tableName.strip()

	return tableName

def getAttribute(statement):
	newAttribute = statement

	newAttribute = newAttribute.replace(',', '')
	newAttribute = newAttribute.lstrip()

	return newAttribute

def getPrimaryKeyAttribute(statement):
	primaryKey = statement
	primaryKey = primaryKey.replace('`', '')
	primaryKey = primaryKey.replace(',', '')
	primaryKey = primaryKey.replace(openParentesis, '')
	primaryKey = primaryKey.replace(closeParentesis, '')
	primaryKey = primaryKey.replace(primaryKeyStatement, '')
	primaryKey = primaryKey.lstrip()

	return primaryKey

def getForeignKeyStatement(key, reference):
	fk = key
	ref = reference

	fk = fk.replace(foreingKeyStatement, '')
	fk = fk.replace(openParentesis, '')
	fk = fk.replace(closeParentesis, '')
	fk = fk.lstrip()	

	ref = ref.replace(openParentesis, '')
	ref = ref.replace(closeParentesis, '')
	ref = ref.replace(referencesStatement, '')
	ref = ref.lstrip()

	tablePart = ref.split(' ')[0].split('.')[1]
	attrPart = ref.split(' ')[1]

	return fk + '.' + tablePart + '.' + attrPart

def addNewTable(table):
	tableDB = tables
	tableDB.append(actualTable)

def addAttributeToTable(attribute, table):
	# Reference to the attributes database
	attributesDB = attributesInTable

	if attributesDB.has_key(table):
		attributesDB[table] = attributesDB[table] + '$' + attribute
	else:
		attributesDB[table] = attribute

def addPrimaryKey(table, primaryKey):
	pkDB = primaryKeyInTable
	pkDB[table] = primaryKey

def addForeignKey(table, foreignKey):
	foreignKeyDB = foreingKeysInTable

	if foreignKeyDB.has_key(table):
		foreignKeyDB[table] = foreignKeyDB[table] + '$' + foreignKey
	else: 
		foreignKeyDB[table] = foreignKey



##############################################
## THE FUN STARTS HERE! 					##
##############################################
fileName = sys.argv[1]
isValidFile = False
fileByLines = open(fileName).read().split('\n')
numLines = len(fileByLines)

actualState = initalState
while not isEndOfFileState(actualState):

	# Define where to stop
	if isEndOfFile():
		actualState = endOfFileState
	else:
		actualLine = currentLine()

	# Detect the CREATE TABLE Statement
	if isInitialState(actualState):
		if hasCreateStament(actualLine):
			actualState = createState
		else: 
			# Take the next line
			actualFileIndex = actualFileIndex + 1

	# Ignore CREATE TABLE and get the table name
	elif isCreateState(actualState):
		tableName = getTableName(actualLine)
		actualTable = tableName
		addNewTable(actualTable)

		# Lets look for the attributes
		actualState = attributeState
		actualFileIndex = actualFileIndex + 1

	# Get the table attributes
	elif isAttributeState(actualState):
		attribute = getAttribute(actualLine)

		# If the actual line has any constraint statements
		if hasConstraint(attribute):
			actualState = constraintState
		
		else:
			# It must be an attribute 
			addAttributeToTable(attribute, actualTable)

			# Could be the table's declaration end
			if isTableDeclarationEnd(attribute):
				actualState = initalState

			actualFileIndex = actualFileIndex + 1

	# Get the constraints
	elif isConstraintState(actualState):

		if isPrimaryKeyConstraint(actualLine):
			primaryKey = getPrimaryKeyAttribute(actualLine)
			addPrimaryKey(actualTable, primaryKey)

			
		elif isForeignKeyConstraint(actualLine):
			# This is bit tricky
			foreingPart = actualLine
			referencesPart = fileByLines[actualFileIndex+1].upper()

			fkStatement = getForeignKeyStatement(foreingPart, referencesPart)
			addForeignKey(actualTable, fkStatement)

		# Could this be the end?
		if isTableDeclarationEnd(actualLine):
			actualState = initalState
			
		actualFileIndex = actualFileIndex + 1


# Print it! Just do it!
generateDBHelper()
