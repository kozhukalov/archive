#include <stdio.h>
#include <stdlib.h>

int** mallocmat(int m, int n){
  int** mat;
  mat = (int**)malloc(sizeof(int*) * m);
  for (int i = 0; i < n; i++){
    mat[i] = (int*)malloc(sizeof(int) * n);
  }
  return mat;
}


int** transpose(int** mat, int m, int n){
  int** transposed;

  transposed = mallocmat(n, m);

  for (int i = 0; i < m; i++){
    for (int j = 0; j < n; j++){
      transposed[j][i] = mat[i][j];
    }
  }
  return transposed;
}


void printmat(int** mat, int m, int n){
  for (int i = 0; i < m; i++){
    for (int j = 0; j < n; j++){
      printf("%d ", mat[i][j]);
    }
    printf("\n");
  }
}


int main(int argc, char** argv){
  const int M=3, N=3;

  int** mat;
  int** transposed;
  mat = mallocmat(M, N);

  mat[0][0] = 1; mat[0][1] = 2; mat[0][2] = 3;
  mat[1][0] = 4; mat[1][1] = 5; mat[1][2] = 6;
  mat[2][0] = 7; mat[2][1] = 8; mat[2][2] = 9;
  printmat(mat, M, N);

  for (int i = 0; i < 1000000; i++){
    transposed = transpose(mat, M, N);
  }
  printmat(transposed, N, M);

  return 0;
}
