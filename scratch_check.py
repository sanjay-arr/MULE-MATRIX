import ast
for file in [
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\backend\app\api\routes\accounts.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\backend\app\api\routes\ml.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\backend\app\schemas\account_schema.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\backend\app\api\router.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\ml\features.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\ml\train.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\ml\evaluate.py",
    r"c:\Users\admin\Mule_Matrix\MULE-MATRIX\ml\predict.py"
]:
    with open(file, "r") as f:
        try:
            ast.parse(f.read())
            print(f"OK: {file}")
        except Exception as e:
            print(f"ERR {file}: {e}")
