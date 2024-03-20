

# * 基姆拉尔森计算公式
# * W= (d+2*m+3*(m+1)/5+y+y/4-y/100+y/400) mod 7
def week(y, m, d):
    if m < 3:
        m += 12
        y = y-1
    w = (d + 2*m + 3*(m + 1)//5 + y + y//4 - y//100 + y//400 + 1) % 7
    return w


print("%d" % week(2019, 9, 15))
print("%d" % week(2015, 4, 16))
print("%d" % week(1989, 2, 3))
print("%d" % week(2024, 3, 20))
print("%d" % week(2006, 4, 4))


# #include <stdio.h>
#
# /*
# * 基姆拉尔森计算公式
# * W= (d+2*m+3*(m+1)/5+y+y/4-y/100+y/400) mod 7
# */
# int week(int y, int m, int d)
# {
#     if (m < 3) {
#         m += 12;
#         y--;
#     }
#
#     int w = (d + 2*m + 3*(m + 1)/5 + y + y/4 - y/100 + y/400 + 1) % 7;
#     return w;
# }
#
# int main()
# {
#     printf("%d\n", week(2019, 9, 15));  //=>0  星期天
#     printf("%d\n", week(2015, 4, 16));  // => 4 星期四
#     printf("%d\n", week(1989, 2, 3));   // => 5 星期五
#     printf("%d\n", week(2024, 3, 20));   // => 5 星期五
#     printf("%d\n", week(2006, 4, 4));   // => 5 星期五
#
#     return 0;
# }
