#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int cmp(const void *a, const void *b) { 
    return *(int *)a - *(int *)b; 
}

int main(int argc, char **argv) {
	MPI_Init(&argc, &argv);
	int comSize, comRank, n, *globalData;
	MPI_Comm_size(MPI_COMM_WORLD, &comSize);
	MPI_Comm_rank(MPI_COMM_WORLD, &comRank);

	if (comRank == 0) {
		printf("Input array size:");
		scanf("%d", &n);
		globalData = malloc(n * sizeof(int));
		for (int i = 0; i < n; ++i)
			globalData[i] = rand() % n;
	}

    double start = MPI_Wtime();
	MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
	int *sendcounts = malloc(comSize * sizeof(int));
    int *displs = malloc(comSize * sizeof(int));
	for (int i = 0, cnt = (n + comSize - 1) / comSize; i < comSize; ++i) {
		displs[i] = i * cnt;
		sendcounts[i] = n - displs[i] < cnt ? n - displs[i] : cnt;
	}
	int *localData = malloc((sendcounts[comRank] + sendcounts[0]) * sizeof(int));
    MPI_Scatterv(globalData, sendcounts, displs, MPI_INT, localData, sendcounts[comRank], MPI_INT, 0, MPI_COMM_WORLD);
	qsort(localData, sendcounts[comRank], sizeof(int), &cmp);
	for (int i = 0; i < comSize; ++i) {
		int partner = comRank + ((i + comRank) % 2 ? 1 : -1);
		if (0 <= partner && partner < comSize) {
			MPI_Sendrecv(localData, sendcounts[comRank], MPI_INT, partner, i, localData + sendcounts[comRank], 
                sendcounts[partner], MPI_INT, partner, i, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			qsort(localData, sendcounts[comRank] + sendcounts[partner], sizeof(int), &cmp);
			if (comRank > partner)
				for (int i = 0; i < sendcounts[comRank]; ++i)
					localData[i] = localData[i + sendcounts[partner]];
		}
	}
    MPI_Gatherv(localData, sendcounts[comRank], MPI_INT, globalData, sendcounts, displs, MPI_INT, 0, MPI_COMM_WORLD);
	free(localData), free(sendcounts), free(displs);
    double end = MPI_Wtime();
	if (comRank == 0) {
        printf("Running time: %lf second\n", end - start);
		// for (int i = 0; i < 100; ++i)
		// 	printf("%d ", globalData[i]);
        // printf("\n");
		free(globalData);
	}
	MPI_Finalize();
}