student_grade = int(input('Enter the mark student:'))

if 91 <= student_grade  <= 100:
    print('Excellent A','',student_grade)
elif 81 <= student_grade <=90:
    print('Fantastic B','',student_grade)

else:
    print('didnt achive pass grade which is B and above')



# النوع الثاني من التحكم في السير الشرطية

match student_grade:
    case grade if 91 <= grade <= 100:
        print('Excellent', '', grade)
    case grade if 81 <= grade <= 90:
        print('Grade B', '', grade)
    case grade if 71 <= grade <= 80:
        print('Grade C', '', grade)

