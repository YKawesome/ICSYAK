from functools import wraps
from gradescope import Gradescope, Course, StudentAssignment, Role
import dotenv


dotenv.load_dotenv()
USERNAME = dotenv.get_key(".env", "GS_USERNAME")
PASSWORD = dotenv.get_key(".env", "GS_PASSWORD")
DEFAULT_ROLE = Role.INSTRUCTOR


# # Decorator to ensure Gradescope session is logged in
# def requires_login(method):
#     @wraps(method)
#     def wrapper(self, *args, **kwargs):
#         if not self.gs.logged_in:
#             self.gs.login()
#         return method(self, *args, **kwargs)
#     return wrapper


# class GradescopeHelper:
#     def __init__(self, username=USERNAME, password=PASSWORD, role=DEFAULT_ROLE):
#         self.gs = Gradescope(username, password)
#         self.role = role

#     @requires_login
#     def get_courses(self) -> list[Course]:
#         return self.gs.get_courses(self.role)

#     @requires_login
#     def get_course_by_id(self, course_id: int) -> Course:
#         courses = self.get_courses()
#         for course in courses:
#             if course.course_id == course_id:
#                 return course
#         raise ValueError(f"Course with ID {course_id} not found.")

#     @requires_login
#     def get_assignments(self, course: Course, only_open=False, as_student: bool = True) -> list[StudentAssignment]:
#         if as_student:
#             assignments = self.gs.get_assignments_as_student(course)
#         else:
#             assignments = self.gs.get_assignments(course)
#         if only_open:
#             return [
#                 assignment for assignment in assignments
#                 if self.is_assignment_open(assignment)
#             ]
#         return assignments

#     @staticmethod
#     def is_assignment_open(assignment: StudentAssignment) -> bool:
#         from datetime import datetime
#         from dateutil.parser import parse
#         try:
#             due = parse(assignment.due_date)
#             return due > datetime.now(due.tzinfo)
#         except Exception:
#             return False

#     @requires_login
#     def get_assignment(self, course: Course, assignment_id: str) -> StudentAssignment:
#         assignments = self.get_assignments(course)
#         for assignment in assignments:
#             if assignment.assignment_id == assignment_id:
#                 return assignment

#     def get_template_url(self, sa: StudentAssignment) -> str:
#         if sa.template_url:
#             return sa.template_url
#         else:
#             raise ValueError("No template PDF available for this assignment.")

#     def get_template_file(self, sa: StudentAssignment):
#         import requests
#         from io import BytesIO

#         if not sa.template_url:
#             raise ValueError("No template PDF available for this assignment.")

#         response = requests.get(sa.template_url)
#         response.raise_for_status()

#         file_obj = BytesIO(response.content)
#         file_obj.name = sa.title + ".pdf"
#         file_obj.seek(0)
#         return file_obj

 
if __name__ == '__main__':
    gs = Gradescope(username=USERNAME, password=PASSWORD)
    gs.login()

    # courses = gs.get_courses(role=DEFAULT_ROLE, as_dict=True)
    courses = gs.get_courses(role=DEFAULT_ROLE)
    print(courses)
