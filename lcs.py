#!/user/bin/env python    
# -*- coding: utf-8 -*-    
    
class arithmetic():    
        
    def __init__(self):    
        pass    
    ''''' 【编辑距离算法】 【levenshtein distance】 【字符串相似度算法】 '''  
      
    def levenshtein(self,first,second):    
        if len(first) > len(second):    
            first,second = second,first    
        if len(first) == 0:    
            return len(second)    
        if len(second) == 0:    
            return len(first)    
        first_length = len(first) + 1    
        second_length = len(second) + 1    
        distance_matrix = [range(second_length) for x in range(first_length)]     
        #print distance_matrix    
        for i in range(1,first_length):    
            for j in range(1,second_length):    
                deletion = distance_matrix[i-1][j] + 1    
                insertion = distance_matrix[i][j-1] + 1    
                substitution = distance_matrix[i-1][j-1]    
                if first[i-1] != second[j-1]:    
                    substitution += 1    
                distance_matrix[i][j] = min(insertion,deletion,substitution)    
        #print distance_matrix    
        return distance_matrix[first_length-1][second_length-1]  
      
    def lcs(self,first,second):    
        first_length = len(first)    
        second_length = len(second)    
        size = 0    
        x = 0    
        y = 0    
        matrix = [range(second_length) for x in range(first_length)]    
        #print matrix    
        for i in range(first_length):    
            for j in range(second_length):    
                #print i,j    
                if first[i] == second[j]:    
                    if i - 1 >= 0 and j - 1 >=0:    
                        matrix[i][j] = matrix[i-1][j-1] + 1    
                    else:    
                        matrix[i][j] = 1    
                    if matrix[i][j] > size:    
                        size = matrix[i][j]    
                        x = j    
                        y = i    
                else:    
                    matrix[i][j] = 0    
        #print matrix    
        #print size,x,y     
    
        return second[x-size+1:x+1]    
        
if __name__ == "__main__":    
    arith = arithmetic()
    print arith.lcs('GUMddddddddddfs','GAMBOL00000000000dfasfasfdafsafasfasdfdsa')