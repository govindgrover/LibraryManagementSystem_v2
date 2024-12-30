# =============================================================================
# =============================== [ Validator ] ===============================
# =============================================================================

class Validator():
	"""
	This class aims to handle the following validations:
		* is_name			->	True iff len > 6
		* is_long_text		->	True iff len > 10
		* is_single_digit	->	True ; obvious
		* is_isbn			->	True iff len == 11
		* is_null			->	False iff !None or len > 0
		* is_date			->	True iff format is 'DD-MM-YYYY'
		* is_float			->	True ; obvious
		* is_uuid			->	True iff len == 36 & n(-) == 4
		* is_email			->	True iff '.' and '@' are present
		* is_password		->	True iff len >= 8

		Direct Database Table(s) used: None
	"""

	def is_name(self, _name: str) -> bool:
		if _name != None and len(_name) >= 4:
			return True
		
		return False

	def is_long_text(self, _txt: str) -> bool:
		if _txt != None and len(_txt) >= 10:
			return True
		
		return False

	def is_single_digit(self, _digit: int) -> bool:
		if _digit != None and type(_digit) == int and (0 <= _digit <= 9):
			return True
		
		return False
	
	def is_isbn(self, _value: str) -> bool:
		if _value != None and len(_value) == 13:
			return True

		return False
	
	def is_null(self, _value: str) -> bool:
		if _value != None and len(_value) > 0:
			return False

		return True
	
	def is_date(self, _value: str) -> bool:
		"""
		Checks for existance of 'DD-MM-YYYY' format only!
		"""

		if not self.is_null(_value):
			tmp = _value.split('-')

			if (len(tmp) == 3
	   			and len(tmp[0]) == 2
	   			and len(tmp[1]) == 2
	   			and len(tmp[2]) == 4
			):
				return True

		return False
	
	def is_float(self, _value: float) -> bool:
		if _value != None:
			if (type(_value) == float or type(_value) == int):
				return True
			else:
				try:
					if float(_value) >= 0:
						return True
				except Exception as e:
					pass

		return False

	def is_int(self, _value: int) -> bool:
		if _value != None and (type(_value) == int or _value == 0.0):
			return True

		return False


	def is_uuid(self, _value: str) -> bool:
		if len(_value) == 36 and len(_value.split('-')) == 5:
			return True

		return False
	
	def is_email(self, _email: str) -> bool:
		if _email is not None and len(_email):
			if '@' in _email and '.' in _email:
				return True

		return False

	def is_password(self, _password: str) -> bool:
		if _password is not None and len(_password) >= 8:
			return True

		return False

	def is_gender(self, _gender: str) -> bool:
		if _gender is not None and len(_gender) == 1:
			if _gender in ('F', 'M'):
				return True

		return False
