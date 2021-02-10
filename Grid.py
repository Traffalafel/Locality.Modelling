class Grid():
    def __init__(self, cell_size, align_boundaries=True):
        self.cells = []
        self.cell_size = cell_size
        self.align_boundaries = align_boundaries

    def get_cell(self, position):
        cells = [cell for cell in self.cells if cell.position == position]
        if len(cells) == 0:
            raise Exception(f"No cell exists for that position: {position}")
        if len(cells) > 1:
            raise Exception(f"Multiple cells exist for that position: {position}")
        else:
            return cells[0]

    def get_heights(self, x_min, x_max, z_min, z_max):

        heights = []

        x_pos_min = x_min // self.cell_size
        x_pos_max = x_max // self.cell_size
        z_pos_min = z_min // self.cell_size
        z_pos_max = z_max // self.cell_size

        z_pos = z_pos_max
        
        while z_pos >= z_pos_min:
            
            cell_top = (z_pos+1)*self.cell_size - 1
            cell_bot = z_pos*self.cell_size
            z_min_cell = max(z_min, cell_bot) % self.cell_size
            z_max_cell = min(z_max, cell_top) % self.cell_size

            z = z_max_cell
            while z >= z_min_cell:

                row_heights = []

                x_pos = x_pos_min
                while x_pos <= x_pos_max:

                    position = (x_pos, z_pos)
                    cell = self.get_cell(position)

                    cell_right = (x_pos+1)*self.cell_size - 1
                    cell_left = x_pos*self.cell_size
                    x_min_cell = max(x_min, cell_left) % self.cell_size
                    x_max_cell = min(x_max, cell_right) % self.cell_size

                    x = x_min_cell
                    while x <= x_max_cell:

                        height = cell.heights[z][x]
                        row_heights.append(height)

                        x += 1
                    x_pos += 1
                z -= 1

                heights.append(row_heights)

            z_pos -= 1

        return heights

    def add_cell(self, cell):

        if len([c for c in self.cells if c.position == cell.position]) > 0:
            raise Exception("A cell already exists for that position")

        n_rows = len(cell.heights)
        n_cols = len(cell.heights[0])
        assert(n_rows == n_cols)

        # Find neighboring cells
        neighbors = self.find_neighbors(cell)

        self.cells.append(cell)
        
        if len(neighbors) == 0:
            return
        
        if not self.align_boundaries:
            return

        # Compute boundary
        diffs = []
        for neighbor in neighbors:
            if abs(cell.position[0]-neighbor.position[0]) == 1:
                if cell.position[0] > neighbor.position[0]:
                    # Neighbor to the left
                    diffs += [cell.heights[row][0] - neighbor.heights[row][n_cols-1] for row in range(n_rows)]
                else:
                    # Neighbor to the right
                    diffs += [cell.heights[row][n_cols-1] - neighbor.heights[row][0] for row in range(n_rows)]
            else:
                if cell.position[1] > neighbor.position[1]:
                    # Neighbor to the bottom
                    diffs += [cell.heights[0][col] - neighbor.heights[n_rows-1][col] for col in range(n_cols)]
                else:
                    # Neighbor to the top
                    diffs += [cell.heights[n_rows-1][col] - neighbor.heights[0][col] for col in range(n_cols)]

        # Align new cell with neighbors
        diff_avg = sum(diffs) / len(diffs)
        for i in range(n_rows):
            for j in range(n_cols):
                cell.heights[i][j] -= diff_avg

    def find_neighbors(self, cell):
        cell_x = cell.position[0]
        cell_y = cell.position[1]
        neighbor_positions = [
            (cell_x-1, cell_y),
            (cell_x+1, cell_y),
            (cell_x, cell_y-1),
            (cell_x, cell_y+1)
        ]
        return [cell for cell in self.cells if cell.position in neighbor_positions]

class Cell():
    def __init__(self, heights, position):
        self.heights = heights
        self.position = position