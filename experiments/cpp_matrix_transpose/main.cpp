#include <iostream>
#include <vector>

std::vector<std::vector<int> > transpose(std::vector<std::vector<int> >& mat){
  std::vector<std::vector<int> > transposed;
  transposed.resize(mat[0].size());
  for (int i = 0; i < mat[0].size(); i++){
    transposed[i].resize(mat.size());
    for (int j = 0; j < mat.size(); j++){
      transposed[i][j] = mat[j][i];
    }
  }
  return transposed;
}

void printmat(std::vector<std::vector<int> >& mat){
  for (int i = 0; i < mat.size(); i++){
    for (int j = 0; j < mat[0].size(); j++){
      std::cout << mat[i][j] << " ";
    }
    std::cout << "\n";
  }
}


int main(int argc, char *argv[]){
  std::vector<std::vector <int> > mat, transposed;

  mat.push_back({1, 2, 3});
  mat.push_back({4, 5, 6});
  mat.push_back({7, 8, 9});

  printmat(mat);

  for (int i = 0; i < 1000000; i++){
    transposed = transpose(mat);
  }
  printmat(transposed);

  return 0;
}
